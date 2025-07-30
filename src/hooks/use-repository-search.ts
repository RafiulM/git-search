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

interface SearchResponse {
  repositories: Repository[];
  total_count: number;
  incomplete_results: boolean;
}

interface UseRepositorySearchParams {
  query: string;
  sort?: string;
  order?: string;
  page?: number;
  per_page?: number;
}

export function useRepositorySearch(params: UseRepositorySearchParams) {
  const { query, sort = 'stars', order = 'desc', page = 1, per_page = 30 } = params;

  return useQuery<SearchResponse>({
    queryKey: ['repository-search', { query, sort, order, page, per_page }],
    queryFn: async () => {
      const searchParams = new URLSearchParams({
        q: query,
        sort,
        order,
        page: page.toString(),
        per_page: per_page.toString(),
      });

      const response = await fetch(`/api/github/search?${searchParams}`);
      if (!response.ok) {
        throw new Error('Failed to search repositories');
      }
      return response.json();
    },
    enabled: !!query?.trim(),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}