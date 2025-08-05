import { useQuery } from '@tanstack/react-query';

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

interface SearchError {
  error: string;
  message: string;
  suggestions?: string[];
  retryAfter?: number;
  response_time_ms?: number;
}

interface UseRepositorySearchParams {
  query: string;
  sort?: string;
  order?: string;
  page?: number;
  per_page?: number;
  language?: string;
  topic?: string;
  stars?: string;
  forks?: string;
  created?: string;
  pushed?: string;
}

export function useRepositorySearch(params: UseRepositorySearchParams) {
  const { 
    query, 
    sort = 'stars', 
    order = 'desc', 
    page = 1, 
    per_page = 30,
    language,
    topic,
    stars,
    forks,
    created,
    pushed
  } = params;

  return useQuery<SearchResponse, Error>({
    queryKey: ['repository-search', { 
      query, sort, order, page, per_page, 
      language, topic, stars, forks, created, pushed 
    }],
    queryFn: async (): Promise<SearchResponse> => {
      const searchParams = new URLSearchParams({
        q: query,
        sort,
        order,
        page: page.toString(),
        per_page: per_page.toString(),
      });

      // Add optional filters
      if (language) searchParams.set('language', language);
      if (topic) searchParams.set('topic', topic);
      if (stars) searchParams.set('stars', stars);
      if (forks) searchParams.set('forks', forks);
      if (created) searchParams.set('created', created);
      if (pushed) searchParams.set('pushed', pushed);

      const response = await fetch(`/api/github/search?${searchParams}`);
      
      if (!response.ok) {
        const errorData: SearchError = await response.json().catch(() => ({
          error: 'Unknown error',
          message: `HTTP ${response.status}: ${response.statusText}`
        }));
        
        if (response.status === 429) {
          const error = new Error('Rate limit exceeded');
          error.name = 'RateLimitError';
          throw error;
        } else if (response.status === 503) {
          const error = new Error(errorData.message || 'GitHub API rate limit exceeded');
          error.name = 'ServiceUnavailable';
          throw error;
        } else if (response.status === 400) {
          const error = new Error(errorData.message || 'Invalid search query');
          error.name = 'ValidationError';
          throw error;
        } else {
          const error = new Error(errorData.message || 'Failed to search repositories');
          error.name = 'SearchError';
          throw error;
        }
      }
      
      return response.json();
    },
    enabled: !!query?.trim(),
    staleTime: 3 * 60 * 1000, // 3 minutes (longer due to caching)
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      // Don't retry rate limit errors
      if (error?.name === 'RateLimitError') return false;
      // Don't retry validation errors
      if (error?.name === 'ValidationError') return false;
      // Retry other errors up to 2 times
      return failureCount < 2;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}