import { useQuery } from '@tanstack/react-query';
import type { Tables } from '@/types/database.types';

interface Repository extends Tables<'repositories'> {
  repository_statistics: Array<{
    total_lines: number;
    total_characters: number;
    file_count: number;
    directory_count: number;
    estimated_tokens_gpt4: number;
    estimated_tokens_claude3: number;
    estimated_tokens_gemini: number;
    storage_size_bytes: number;
    language_breakdown: Record<string, number>;
    file_type_breakdown: Record<string, number>;
    largest_files: Array<{ path: string; size: number }>;
    complexity_score: number;
    maintainability_index: number;
    calculated_at: string;
  }>;
  repository_documentation: Array<{
    doc_type: string;
    title: string;
    content: string;
    mermaid_diagram: string;
    generated_at: string;
  }>;
  repository_files: Array<{
    file_path: string;
    file_name: string;
    file_extension: string;
    file_size_bytes: number;
    line_count: number;
    character_count: number;
    language: string;
    is_binary: boolean;
  }>;
}

export function useRepositoryDetails(repositoryId: string) {
  return useQuery<{ repository: Repository }>({
    queryKey: ['repository-details', repositoryId],
    queryFn: async () => {
      const response = await fetch(`/api/github/repository/${repositoryId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch repository details');
      }
      return response.json();
    },
    enabled: !!repositoryId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}