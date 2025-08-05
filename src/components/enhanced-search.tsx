"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Search, Filter, X, Loader2, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';

interface SearchFilters {
  sort: string;
  order: string;
  language?: string;
  topic?: string;
  stars?: string;
  forks?: string;
  created?: string;
  pushed?: string;
}

interface EnhancedSearchProps {
  query: string;
  onQueryChange: (query: string) => void;
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onSearch: () => void;
  isLoading: boolean;
  error?: Error | null;
  className?: string;
}

const LANGUAGES = [
  'JavaScript', 'TypeScript', 'Python', 'Java', 'C++', 'C#', 'Go', 'Rust',
  'PHP', 'Ruby', 'Swift', 'Kotlin', 'Dart', 'HTML', 'CSS', 'Shell'
];

const TOPICS = [
  'machine-learning', 'web-development', 'mobile-app', 'game-development',
  'data-science', 'artificial-intelligence', 'blockchain', 'devops',
  'frontend', 'backend', 'fullstack', 'api', 'microservices', 'docker'
];

const STAR_RANGES = [
  { label: 'Any', value: '' },
  { label: '1+', value: '>=1' },
  { label: '10+', value: '>=10' },
  { label: '100+', value: '>=100' },
  { label: '1k+', value: '>=1000' },
  { label: '10k+', value: '>=10000' },
];

const FORK_RANGES = [
  { label: 'Any', value: '' },
  { label: '1+', value: '>=1' },
  { label: '5+', value: '>=5' },
  { label: '50+', value: '>=50' },
  { label: '500+', value: '>=500' },
];

const DATE_RANGES = [
  { label: 'Any time', value: '' },
  { label: 'Past week', value: '>=2024-01-01' },
  { label: 'Past month', value: '>=2023-12-01' },
  { label: 'Past year', value: '>=2023-01-01' },
  { label: '2+ years ago', value: '<2022-01-01' },
];

export function EnhancedSearch({
  query,
  onQueryChange,
  filters,
  onFiltersChange,
  onSearch,
  isLoading,
  error,
  className = ''
}: EnhancedSearchProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const SEARCH_SUGGESTIONS = [
    'react typescript',
    'machine learning python',
    'web framework javascript',
    'mobile app react-native',
    'blockchain ethereum',
    'data visualization d3',
    'api nodejs express',
    'ui components react',
    'game engine unity',
    'devops docker kubernetes'
  ];

  useEffect(() => {
    if (query.length > 0) {
      const filtered = SEARCH_SUGGESTIONS
        .filter(suggestion => 
          suggestion.toLowerCase().includes(query.toLowerCase()) &&
          suggestion.toLowerCase() !== query.toLowerCase()
        )
        .slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    onSearch();
  };

  const handleFilterChange = (key: keyof SearchFilters, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined
    });
  };

  const clearFilter = (key: keyof SearchFilters) => {
    const newFilters = { ...filters };
    delete newFilters[key];
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      sort: filters.sort,
      order: filters.order
    });
  };

  const hasActiveFilters = Object.keys(filters).some(key => 
    key !== 'sort' && key !== 'order' && filters[key as keyof SearchFilters]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const selectSuggestion = (suggestion: string) => {
    onQueryChange(suggestion);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Main Search Bar */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <Input
                ref={inputRef}
                type="text"
                placeholder="Search repositories (e.g., react typescript, machine learning python)"
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                className="pl-10 h-12 text-base"
                disabled={isLoading}
                aria-label="Search repositories"
                aria-expanded={showSuggestions}
                aria-haspopup="listbox"
                role="combobox"
              />
              {query && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                  onClick={() => {
                    onQueryChange('');
                    setShowSuggestions(false);
                  }}
                  aria-label="Clear search"
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>

            {/* Search Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <Card 
                ref={suggestionsRef}
                className="absolute top-full left-0 right-0 z-50 mt-1 shadow-lg"
              >
                <CardContent className="p-2">
                  <div role="listbox" aria-label="Search suggestions">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={suggestion}
                        type="button"
                        className="w-full text-left px-3 py-2 rounded hover:bg-muted focus:bg-muted focus:outline-none text-sm"
                        onClick={() => selectSuggestion(suggestion)}
                        role="option"
                        aria-selected={false}
                      >
                        <Search className="w-3 h-3 inline mr-2 text-muted-foreground" />
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <Button 
            type="submit" 
            size="lg" 
            className="h-12 px-8"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Searching...
              </>
            ) : (
              'Search'
            )}
          </Button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error.message === 'Rate limit exceeded' ? (
              <>
                Too many requests. Please wait a moment before searching again.
                <br />
                <small className="text-xs mt-1 block">
                  Try using more specific search terms to get better results.
                </small>
              </>
            ) : error.message === 'GitHub API rate limit exceeded' ? (
              <>
                GitHub API rate limit reached. Please try again later.
                <br />
                <small className="text-xs mt-1 block">
                  Consider searching during off-peak hours for better availability.
                </small>
              </>
            ) : (
              error.message || 'An error occurred while searching. Please try again.'
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Basic Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <Label className="text-sm font-medium">Sort by:</Label>
        </div>
        
        <Select value={filters.sort} onValueChange={(value) => handleFilterChange('sort', value)}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="stars">Stars</SelectItem>
            <SelectItem value="forks">Forks</SelectItem>
            <SelectItem value="updated">Updated</SelectItem>
            <SelectItem value="created">Created</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filters.order} onValueChange={(value) => handleFilterChange('order', value)}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Descending</SelectItem>
            <SelectItem value="asc">Ascending</SelectItem>
          </SelectContent>
        </Select>

        <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
          <CollapsibleTrigger asChild>
            <Button variant="outline" size="sm">
              Advanced Filters
              {showAdvanced ? (
                <ChevronUp className="w-4 h-4 ml-1" />
              ) : (
                <ChevronDown className="w-4 h-4 ml-1" />
              )}
            </Button>
          </CollapsibleTrigger>
        </Collapsible>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {filters.language && (
            <Badge variant="secondary" className="gap-1">
              Language: {filters.language}
              <button
                onClick={() => clearFilter('language')}
                className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                aria-label={`Remove ${filters.language} language filter`}
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.topic && (
            <Badge variant="secondary" className="gap-1">
              Topic: {filters.topic}
              <button
                onClick={() => clearFilter('topic')}
                className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                aria-label={`Remove ${filters.topic} topic filter`}
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.stars && (
            <Badge variant="secondary" className="gap-1">
              Stars: {filters.stars}
              <button
                onClick={() => clearFilter('stars')}
                className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                aria-label="Remove stars filter"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.forks && (
            <Badge variant="secondary" className="gap-1">
              Forks: {filters.forks}
              <button
                onClick={() => clearFilter('forks')}
                className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                aria-label="Remove forks filter"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="text-muted-foreground"
          >
            Clear all
          </Button>
        </div>
      )}

      {/* Advanced Filters */}
      <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
        <CollapsibleContent className="space-y-4">
          <Separator />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Language Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Language</Label>
              <Select 
                value={filters.language || ''} 
                onValueChange={(value) => handleFilterChange('language', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any language</SelectItem>
                  {LANGUAGES.map(lang => (
                    <SelectItem key={lang} value={lang.toLowerCase()}>
                      {lang}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Topic Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Topic</Label>
              <Select 
                value={filters.topic || ''} 
                onValueChange={(value) => handleFilterChange('topic', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any topic" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any topic</SelectItem>
                  {TOPICS.map(topic => (
                    <SelectItem key={topic} value={topic}>
                      {topic}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Stars Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Stars</Label>
              <Select 
                value={filters.stars || ''} 
                onValueChange={(value) => handleFilterChange('stars', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any stars" />
                </SelectTrigger>
                <SelectContent>
                  {STAR_RANGES.map(range => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Forks Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Forks</Label>
              <Select 
                value={filters.forks || ''} 
                onValueChange={(value) => handleFilterChange('forks', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any forks" />
                </SelectTrigger>
                <SelectContent>
                  {FORK_RANGES.map(range => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Created Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Created</Label>
              <Select 
                value={filters.created || ''} 
                onValueChange={(value) => handleFilterChange('created', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any time" />
                </SelectTrigger>
                <SelectContent>
                  {DATE_RANGES.map(range => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Last Updated Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Last Updated</Label>
              <Select 
                value={filters.pushed || ''} 
                onValueChange={(value) => handleFilterChange('pushed', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any time" />
                </SelectTrigger>
                <SelectContent>
                  {DATE_RANGES.map(range => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}