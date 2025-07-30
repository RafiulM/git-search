"use client";

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, Filter, Star, GitFork, Eye, Calendar, FileText, BarChart3, Heart, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '@/components/theme-toggle';
// Authentication removed
import Link from 'next/link';

interface Repository {
  id: number;
  full_name: string;
  name: string;
  description: string;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  watchers_count: number;
  language: string;
  topics: string[];
  updated_at: string;
  size: number;
  analysis?: {
    statistics: unknown[];
    documentation: unknown[];
    last_analyzed: string;
  };
}

interface SearchResponse {
  repositories: Repository[];
  total_count: number;
  incomplete_results: boolean;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [sort, setSort] = useState('stars');
  const [order, setOrder] = useState('desc');
  const [page, setPage] = useState(1);

  const performSearch = useCallback(async (searchQuery: string, currentPage = 1) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: searchQuery,
        sort,
        order,
        page: currentPage.toString(),
        per_page: '30',
      });

      const response = await fetch(`/api/github/search?${params}`);
      const data = await response.json();
      
      if (response.ok) {
        setSearchResults(data);
      } else {
        console.error('Search failed:', data.error);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  }, [sort, order]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      performSearch(q);
    }
  }, [searchParams, performSearch]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    performSearch(query, 1);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const analyzeRepository = async (repo: Repository) => {
    try {
      const [owner, name] = repo.full_name.split('/');
      const response = await fetch('/api/github/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ owner, repo: name }),
      });
      
      if (response.ok) {
        performSearch(query, page);
      }
    } catch (error) {
      console.error('Analysis error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </div>
            </Link>
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Search Form */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search repositories (e.g., react typescript, machine learning python)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </form>

          {/* Sort Controls */}
          <div className="flex gap-4 items-center">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              <span className="text-sm">Sort by:</span>
            </div>
            <Select value={sort} onValueChange={setSort}>
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
            <Select value={order} onValueChange={setOrder}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Descending</SelectItem>
                <SelectItem value="asc">Ascending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Results */}
        {loading && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-6 w-1/3 mb-2" />
                  <Skeleton className="h-4 w-full mb-4" />
                  <div className="flex gap-4">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {searchResults && !loading && (
          <>
            <div className="mb-6">
              <p className="text-sm text-muted-foreground">
                Found {formatNumber(searchResults.total_count)} repositories
                {searchResults.incomplete_results && ' (results may be incomplete)'}
              </p>
            </div>

            <div className="space-y-4">
              {searchResults.repositories.map((repo) => (
                <Card key={repo.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Link 
                            href={`/repository/${repo.full_name.replace('/', '-')}`}
                            className="text-xl font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {repo.full_name}
                          </Link>
                          <a
                            href={repo.html_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                        
                        <p className="text-muted-foreground mb-3 line-clamp-2">
                          {repo.description || 'No description available'}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-3">
                          {repo.language && (
                            <Badge variant="secondary">{repo.language}</Badge>
                          )}
                          {repo.topics?.slice(0, 3).map((topic) => (
                            <Badge key={topic} variant="outline">
                              {topic}
                            </Badge>
                          ))}
                          {repo.topics?.length > 3 && (
                            <Badge variant="outline">
                              +{repo.topics.length - 3} more
                            </Badge>
                          )}
                        </div>

                        <div className="flex items-center gap-6 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4" />
                            {formatNumber(repo.stargazers_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <GitFork className="w-4 h-4" />
                            {formatNumber(repo.forks_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            {formatNumber(repo.watchers_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            Updated {formatDate(repo.updated_at)}
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 ml-4">
                        {repo.analysis?.statistics && repo.analysis.statistics.length > 0 ? (
                          <Link href={`/repository/${repo.full_name.replace('/', '-')}`}>
                            <Button variant="outline" size="sm">
                              <BarChart3 className="w-4 h-4 mr-1" />
                              View Analysis
                            </Button>
                          </Link>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => analyzeRepository(repo)}
                          >
                            <FileText className="w-4 h-4 mr-1" />
                            Analyze
                          </Button>
                        )}
                        
                        {repo.analysis?.last_analyzed && (
                          <p className="text-xs text-muted-foreground text-center">
                            Analyzed {formatDate(repo.analysis.last_analyzed)}
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {searchResults.total_count > 30 && (
              <div className="mt-8 flex justify-center gap-2">
                <Button
                  variant="outline"
                  disabled={page === 1}
                  onClick={() => {
                    const newPage = page - 1;
                    setPage(newPage);
                    performSearch(query, newPage);
                  }}
                >
                  Previous
                </Button>
                <span className="flex items-center px-4 text-sm">
                  Page {page}
                </span>
                <Button
                  variant="outline"
                  disabled={page * 30 >= searchResults.total_count}
                  onClick={() => {
                    const newPage = page + 1;
                    setPage(newPage);
                    performSearch(query, newPage);
                  }}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}

        {searchResults && searchResults.repositories.length === 0 && !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-2">No repositories found</h3>
              <p className="text-muted-foreground">
                Try adjusting your search terms or filters
              </p>
            </CardContent>
          </Card>
        )}

        {!searchResults && !loading && query && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">👋</div>
              <h3 className="text-xl font-semibold mb-2">Welcome to Git Search</h3>
              <p className="text-muted-foreground mb-4">
                Search GitHub repositories and get detailed analysis including:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto text-left">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <BarChart3 className="w-4 h-4 text-blue-500" />
                    Lines of code & token estimates
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <FileText className="w-4 h-4 text-green-500" />
                    Project documentation
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Star className="w-4 h-4 text-yellow-500" />
                    Tech stack analysis
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <GitFork className="w-4 h-4 text-purple-500" />
                    Architecture flowcharts
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}