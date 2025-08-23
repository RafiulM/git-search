import { notFound } from 'next/navigation';
import { RepositoryHeader } from '@/components/repository-header';
import { RepositoryTabs } from '@/components/repository-tabs';
import { listRepositories, getRepositoryDocuments } from '@/lib/api';
import type { Repository, RepositoryAnalysis, Document, DocumentsResponse } from '@/lib/types/api';

// ISR Configuration
export const revalidate = 3600; // Revalidate every hour

// Generate static params for popular repositories with analysis data
export async function generateStaticParams() {
  try {
    const response = await listRepositories({
      limit: 25, // Generate static pages for top 25 repositories  
      include_analysis: true // Include analysis data to ensure we have rich content
    });

    const params = response.repositories.map((repo) => {
      // Extract owner/repo from GitHub URL
      try {
        const url = new URL(repo.repo_url);
        const pathParts = url.pathname.split('/').filter(Boolean);
        if (pathParts.length >= 2) {
          return {
            owner: pathParts[0],
            repo: pathParts[1]
          };
        }
      } catch (error) {
        console.error('Error parsing repo URL:', repo.repo_url, error);
      }
      return null;
    }).filter(Boolean);

    console.log(`Generated ${params.length} static params for repository pages`);
    return params;
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}

interface RepositoryPageProps {
  params: Promise<{
    owner: string;
    repo: string;
  }>;
}

export default async function RepositoryPage({ params }: RepositoryPageProps) {
  const { owner, repo } = await params;
  
  // Construct repo URL from owner and repo parameters
  const repoUrl = `https://github.com/${owner}/${repo}`;
  
  // Fetch repository by repo_url using search
  let repository: Repository;
  try {
    const response = await listRepositories({
      search: repoUrl,
      include_analysis: true,
      include_ai_summary: false,
      limit: 1
    });
    
    if (response.repositories.length === 0) {
      notFound();
    }
    
    repository = response.repositories[0] as Repository;
  } catch (error: unknown) {
    console.error('Error fetching repository:', error);
    notFound();
  }

  // Get analysis from repository if available
  const repositoryAnalysis: RepositoryAnalysis | null = repository.analysis || null;

  // Fetch documents using API
  let documentsResponse: DocumentsResponse | undefined;
  let documents: Document[] = [];
  let firstDocumentType = '';
  
  try {
    documentsResponse = await getRepositoryDocuments(repository.id, {
      current_only: true
    }) as DocumentsResponse;
    documents = documentsResponse?.documents || [];

    
    // Get unique document types for documentation navigation
    const documentTypes = Array.from(new Set(documents.map(doc => doc.document_type)));

    if (documentTypes.length === 0) {
      firstDocumentType = 'readme';
    } else {
      firstDocumentType = documentTypes[0];
    }
  } catch (error: unknown) {
    console.error('Error fetching documents:', error);
  }

  return (
    <>
      <RepositoryHeader
        repository={repository}
        owner={owner}
        repo={repo}
        firstDocumentType={firstDocumentType}
      >
        <RepositoryTabs
          repository={repository}
          analysis={repositoryAnalysis}
          owner={owner}
          repo={repo}
          firstDocumentType={firstDocumentType}
        />
      </RepositoryHeader>
    </>
  );
}