import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface FavoriteRepository {
  id: string;
  name: string;
  repo_url: string;
  author: string | null;
  branch: string | null;
  created_at: string;
  updated_at: string;
  files_processed: number | null;
  total_files_found: number | null;
  total_lines: number | null;
  estimated_tokens: number | null;
  favorite_count: number;
  analysis_created_at: string | null;
}

export function useFavorites() {
  return useQuery<FavoriteRepository[]>({
    queryKey: ['favorites'],
    queryFn: async () => {
      const response = await fetch('/api/github/favorites');
      if (!response.ok) {
        throw new Error('Failed to fetch favorites');
      }
      return response.json();
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useAddFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (repositoryId: string) => {
      const response = await fetch('/api/github/favorites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_id: repositoryId,
          user_id: 'anonymous'
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to add favorite');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
    },
  });
}

export function useRemoveFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (repositoryId: string) => {
      const response = await fetch(
        `/api/github/favorites?repository_id=${repositoryId}&user_id=anonymous`,
        {
          method: 'DELETE',
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to remove favorite');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['repositories'] });
    },
  });
}