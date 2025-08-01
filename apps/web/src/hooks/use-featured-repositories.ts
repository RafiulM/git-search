import { useQuery } from '@tanstack/react-query';
import { createSupabaseServerClient } from '@/lib/supabase';
import type { Tables } from '@/types/database.types';

interface FeaturedRepository {
  id: string;
  name: string;
  description: string | null;
  repo_url: string;
  author: string | null;
  branch: string | null;
  created_at: string;
  updated_at: string;
  // Add estimated stats based on repository_analysis
  stats?: {
    total_lines: number;
    total_characters: number;
    total_files_found: number;
    estimated_tokens: number;
    estimated_size_bytes: number;
  };
}

export function useFeaturedRepositories(limit: number = 4) {
  return useQuery<FeaturedRepository[]>({
    queryKey: ['featured-repositories', limit],
    queryFn: async () => {
      // This would be called from a server component or API route
      // For client-side usage, we'll need to create an API endpoint
      const response = await fetch(`/api/repositories/featured?limit=${limit}`);
      if (!response.ok) {
        throw new Error('Failed to fetch featured repositories');
      }
      return response.json();
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}