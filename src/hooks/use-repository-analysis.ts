import { useMutation, useQueryClient } from '@tanstack/react-query';

interface AnalyzeRepositoryParams {
  owner: string;
  repo: string;
}

interface AnalyzeRepositoryResponse {
  repository: {
    id: string;
    full_name: string;
  };
  message: string;
}

export function useRepositoryAnalysis() {
  const queryClient = useQueryClient();

  return useMutation<AnalyzeRepositoryResponse, Error, AnalyzeRepositoryParams>({
    mutationFn: async ({ owner, repo }) => {
      const response = await fetch('/api/github/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ owner, repo }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze repository');
      }

      return response.json();
    },
    onSuccess: (data) => {
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['repository-search'] });
      queryClient.invalidateQueries({ queryKey: ['repository-details', data.repository.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });
}