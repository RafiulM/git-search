import { useMutation, useQueryClient } from '@tanstack/react-query';

interface GenerateDocumentationParams {
  repository_id: string;
  doc_type: string;
}

interface GenerateDocumentationResponse {
  message: string;
  documentation: {
    id: string;
    title: string;
    content: string;
    mermaid_diagram?: string;
  };
}

export function useRepositoryDocumentation() {
  const queryClient = useQueryClient();

  return useMutation<GenerateDocumentationResponse, Error, GenerateDocumentationParams>({
    mutationFn: async ({ repository_id, doc_type }) => {
      const response = await fetch('/api/github/documentation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repository_id, doc_type }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate documentation');
      }

      return response.json();
    },
    onSuccess: (_, variables) => {
      // Invalidate repository details to refresh documentation
      queryClient.invalidateQueries({ 
        queryKey: ['repository-details', variables.repository_id] 
      });
    },
  });
}