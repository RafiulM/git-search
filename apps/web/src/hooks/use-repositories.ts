import { useQuery } from '@tanstack/react-query';
import type { Tables } from '@/types/database.types';

type Repository = Tables<'repositories'>;

export function useRepositories() {
  return useQuery<Repository[]>({
    queryKey: ['repositories'],
    queryFn: async () => {
      const response = await fetch('/api/repositories');
      if (!response.ok) {
        throw new Error('Failed to fetch repositories');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}