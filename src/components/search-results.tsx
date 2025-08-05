"use client";

import React from 'react';
import { 
  Star, 
  GitFork, 
  Calendar, 
  FileText, 
  BarChart3, 
  ExternalLink, 
  Clock,
  Zap,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination';
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

interface SearchMeta {
  cached: boolean;
  response_time_ms: number;
  rate_limit: {
    remaining: number;
    reset_at: number;
  };
}

interface SearchResponse {
  repositories: Repository[];
  total_count: number;
  incomplete_results: boolean;
  search_query?: string;
  filters?: Record<string, any>;
  meta?: SearchMeta;
}

interface SearchResultsProps {
  data?: SearchResponse;
  isLoading: boolean;
  error?: Error | null;
  page: number;
  onPageChange: (page: number) => void;
  perPage?: number;
  onAnalyzeRepository?: (repo: Repository) => void;
  isAnalyzing?: boolean;
  className?: string;
}

export function SearchResults({
  data,
  isLoading,
  error,
  page,
  onPageChange,
  perPage = 30,
  onAnalyzeRepository,
  isAnalyzing = false,
  className = ''
}: SearchResultsProps) {
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
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  const getLanguageColor = (language: string) => {
    const colors: Record<string, string> = {
      'JavaScript': 'bg-yellow-500',
      'TypeScript': 'bg-blue-600',
      'Python': 'bg-blue-500',
      'Java': 'bg-orange-600',
      'C++': 'bg-blue-700',
      'C#': 'bg-purple-600',
      'Go': 'bg-cyan-500',
      'Rust': 'bg-orange-700',
      'PHP': 'bg-indigo-600',
      'Ruby': 'bg-red-600',
      'Swift': 'bg-orange-500',
      'Kotlin': 'bg-purple-500',
    };
    return colors[language] || 'bg-gray-500';
  };

  const totalPages = data ? Math.ceil(data.total_count / perPage) : 0;

  // Loading State
  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="flex items-center justify-between">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-6 w-2/3" />
                  <Skeleton className="h-8 w-20" />
                </div>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <div className="flex gap-2">
                  <Skeleton className="h-5 w-16" />
                  <Skeleton className="h-5 w-20" />
                  <Skeleton className="h-5 w-18" />
                </div>
                <div className="flex gap-4 text-sm">
                  <Skeleton className="h-4 w-12" />
                  <Skeleton className="h-4 w-12" />
                  <Skeleton className="h-4 w-20" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Error State
  if (error && !data) {
    return (
      <div className={className}>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {error.message || 'An error occurred while searching repositories.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // No Data State
  if (!data || data.repositories.length === 0) {
    return (
      <div className={className}>
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2">No repositories found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search terms or filters to find what you&apos;re looking for.
            </p>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>Suggestions:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Use more general keywords</li>
                <li>Remove some filters</li>
                <li>Check for typos in your search query</li>
                <li>Try different programming languages or topics</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Results Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">
            Found {formatNumber(data.total_count)} repositories
            {data.incomplete_results && (
              <span className="text-amber-600"> (results may be incomplete)</span>
            )}
          </p>
          {data.meta && (
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {data.meta.response_time_ms}ms
              </div>
              {data.meta.cached && (
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  Cached
                </div>
              )}
              <div className="flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {data.meta.rate_limit.remaining} requests left
              </div>
            </div>
          )}
        </div>
        
        {data.search_query && (
          <div className="text-sm text-muted-foreground">
            Query: <code className="bg-muted px-1 rounded text-xs">{data.search_query}</code>
          </div>
        )}
      </div>

      {/* Results List */}
      <div className="space-y-3" role="list" aria-label="Search results">
        {data.repositories.map((repo) => (
          <Card 
            key={repo.id} 
            className="hover:shadow-lg transition-all duration-200 hover:border-primary/20"
            role="listitem"
          >
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                  {/* Repository Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <Link 
                        href={`/repository/${repo.full_name.replace('/', '-')}`}
                        className="text-lg font-semibold text-primary hover:text-primary/80 transition-colors truncate"
                        title={repo.full_name}
                      >
                        {repo.full_name}
                      </Link>
                      <a
                        href={repo.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors flex-shrink-0"
                        aria-label={`Open ${repo.full_name} on GitHub`}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                    
                    {/* Repository Stats */}
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div 
                        className="flex items-center gap-1"
                        title={`${repo.stargazers_count} stars`}
                      >
                        <Star className="w-3 h-3" />
                        <span>{formatNumber(repo.stargazers_count)}</span>
                      </div>
                      <div 
                        className="flex items-center gap-1"
                        title={`${repo.forks_count} forks`}
                      >
                        <GitFork className="w-3 h-3" />
                        <span>{formatNumber(repo.forks_count)}</span>
                      </div>
                      <div 
                        className="flex items-center gap-1"
                        title={`Updated ${repo.updated_at}`}
                      >
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(repo.updated_at)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Description */}
                  <p className="text-muted-foreground text-sm mb-3 line-clamp-2">
                    {repo.description || 'No description available'}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-2">
                    {repo.language && (
                      <Badge 
                        variant="secondary" 
                        className="text-xs flex items-center gap-1"
                      >
                        <div 
                          className={`w-2 h-2 rounded-full ${getLanguageColor(repo.language)}`}
                          aria-hidden="true"
                        />
                        {repo.language}
                      </Badge>
                    )}
                    {repo.topics?.slice(0, 3).map((topic) => (
                      <Badge key={topic} variant="outline" className="text-xs">
                        {topic}
                      </Badge>
                    ))}
                    {repo.topics && repo.topics.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{repo.topics.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col gap-2 ml-6 flex-shrink-0">
                  {repo.analysis?.statistics && repo.analysis.statistics.length > 0 ? (
                    <Link href={`/repository/${repo.full_name.replace('/', '-')}`}>
                      <Button variant="outline" size="sm" className="w-full">
                        <BarChart3 className="w-4 h-4 mr-1" />
                        View Analysis
                      </Button>
                    </Link>
                  ) : onAnalyzeRepository ? (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onAnalyzeRepository(repo)}
                      disabled={isAnalyzing}
                      className="w-full"
                    >
                      <FileText className="w-4 h-4 mr-1" />
                      {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                    </Button>
                  ) : null}
                  
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
      {totalPages > 1 && (
        <div className="flex justify-center">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  onClick={() => onPageChange(Math.max(1, page - 1))}
                  className={page === 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                  aria-disabled={page === 1}
                />
              </PaginationItem>
              
              {/* Show first page */}
              {page > 3 && (
                <>
                  <PaginationItem>
                    <PaginationLink 
                      onClick={() => onPageChange(1)}
                      className="cursor-pointer"
                    >
                      1
                    </PaginationLink>
                  </PaginationItem>
                  {page > 4 && (
                    <PaginationItem>
                      <span className="px-3 py-2">...</span>
                    </PaginationItem>
                  )}
                </>
              )}
              
              {/* Show pages around current page */}
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = Math.max(1, Math.min(totalPages, page - 2 + i));
                if (pageNum < 1 || pageNum > totalPages) return null;
                if (page > 3 && pageNum === 1) return null;
                if (page < totalPages - 2 && pageNum === totalPages) return null;
                
                return (
                  <PaginationItem key={pageNum}>
                    <PaginationLink
                      onClick={() => onPageChange(pageNum)}
                      isActive={pageNum === page}
                      className="cursor-pointer"
                      aria-current={pageNum === page ? 'page' : undefined}
                    >
                      {pageNum}
                    </PaginationLink>
                  </PaginationItem>
                );
              })}
              
              {/* Show last page */}
              {page < totalPages - 2 && (
                <>
                  {page < totalPages - 3 && (
                    <PaginationItem>
                      <span className="px-3 py-2">...</span>
                    </PaginationItem>
                  )}
                  <PaginationItem>
                    <PaginationLink 
                      onClick={() => onPageChange(totalPages)}
                      className="cursor-pointer"
                    >
                      {totalPages}
                    </PaginationLink>
                  </PaginationItem>
                </>
              )}
              
              <PaginationItem>
                <PaginationNext 
                  onClick={() => onPageChange(Math.min(totalPages, page + 1))}
                  className={page === totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                  aria-disabled={page === totalPages}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
      
      {/* Results Footer */}
      {data.repositories.length > 0 && (
        <div className="text-center text-sm text-muted-foreground">
          Showing {(page - 1) * perPage + 1} to {Math.min(page * perPage, data.total_count)} of {formatNumber(data.total_count)} results
        </div>
      )}
    </div>
  );
}