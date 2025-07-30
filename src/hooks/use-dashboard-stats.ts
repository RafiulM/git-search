import { useQuery } from '@tanstack/react-query';

interface DashboardStats {
  totalRepositories: number;
  totalAnalyzed: number;
  totalLines: number;
  totalFiles: number;
  averageComplexity: number;
  topLanguages: Array<{ language: string; count: number; percentage: number }>;
  recentAnalyses: Array<{
    repository: {
      full_name: string;
      stars_count: number;
      language: string;
    };
    analyzed_at: string;
  }>;
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await fetch('/api/dashboard/stats');
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard stats');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}