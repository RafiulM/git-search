import { notFound } from 'next/navigation';
import { FileText } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent } from '@/components/ui/tabs';
import { GenerateDocsButtons } from '@/components/generate-docs-buttons';
import { MobileDocumentationLayout } from '@/components/mobile-documentation-layout';
import { RepositoryHeader } from '@/components/repository-header';
import { RepositoryTabs } from '@/components/repository-tabs';
import { marked } from 'marked';
import { getRepositoryDocuments, listRepositories } from '@/lib/api';
import type { Repository as TypedRepository, Document, RepositoriesResponse, DocumentsResponse, Repository as ApiRepository } from '@/lib/types/api';
import type { Tables } from '@/types/database.types';

// ISR Configuration
export const revalidate = 3600; // Revalidate every hour

// Generate static params for popular repository docs using the specific documents endpoint
export async function generateStaticParams() {
  try {
    // Fetch repositories that have analysis/documents available
    const response = await listRepositories({
      limit: 15, // Generate static pages for top 15 repositories
      include_analysis: true // Only get repos with analysis
    });

    const params = [];
    
    for (const repo of response.repositories) {
      try {
        // Extract owner/repo from GitHub URL
        const url = new URL(repo.repo_url);
        const pathParts = url.pathname.split('/').filter(Boolean);
        if (pathParts.length >= 2) {
          const owner = pathParts[0];
          const repoName = pathParts[1];

          // Use the existing getRepositoryDocuments function instead of direct fetch
          try {
            const docsResponse = await getRepositoryDocuments(repo.id, {
              current_only: true,
              summary_only: true
            });
            
            if (docsResponse?.documents && docsResponse.documents.length > 0) {
              // Get unique document types
              const documentTypes = Array.from(new Set(docsResponse.documents.map((doc: any) => doc.document_type)));
              console.log(`Found ${documentTypes.length} document types for ${owner}/${repoName}:`, documentTypes);
              
              // Add params for each document type found
              for (const docType of documentTypes) {
                params.push({
                  owner,
                  repo: repoName,
                  document_type: docType
                });
              }
            } else {
              console.log(`No documents found for ${owner}/${repoName}, adding fallback types`);
              // If no documents found, add common document types as fallback
              params.push(
                { owner, repo: repoName, document_type: 'readme' },
                { owner, repo: repoName, document_type: 'api' }
              );
            }
          } catch (docError) {
            console.error('Error fetching documents for repo:', repo.id, docError);
            // Add fallback document types
            params.push(
              { owner, repo: repoName, document_type: 'readme' },
              { owner, repo: repoName, document_type: 'api' }
            );
          }
        }
      } catch (urlError) {
        console.error('Error parsing repo URL:', repo.repo_url, urlError);
      }
    }

    console.log(`Generated ${params.length} static params for docs pages`);
    return params;
  } catch (error) {
    console.error('Error generating static params for docs:', error);
    return [];
  }
}

// Configure marked with GFM support
marked.setOptions({
  gfm: true,
  breaks: true,
});


interface DocsPageProps {
  params: Promise<{
    owner: string;
    repo: string;
    document_type: string;
  }>;
}

export default async function DocsPage({ params }: DocsPageProps) {
  const { owner, repo, document_type } = await params;
  
  // Construct repo URL from owner and repo parameters
  const repoUrl = `https://github.com/${owner}/${repo}`;
  
  // Fetch repository by repo_url
  let repository: TypedRepository;
  try {
    const repositoriesResponse = await listRepositories({
      search: repoUrl,
      include_analysis: false,
      include_ai_summary: true,
      limit: 1
    });

    repository = repositoriesResponse.repositories[0] as TypedRepository;
  } catch (error) {
    console.error('Error fetching repository:', error);
    notFound();
  }

  // Fetch documents for this repository and document type using the new API endpoint
  let documentsResponse: DocumentsResponse | undefined;
  try {
    documentsResponse = await getRepositoryDocuments(repository.id, {
      document_type,
      current_only: true,
      summary_only: false
    }) as DocumentsResponse;
  } catch (error) {
    console.error('Error fetching documents:', error);
  }

  const documents: Document[] = documentsResponse?.documents || [];
  
  // Filter documents by type (already filtered by API, but keep for safety)
  const filteredDocuments = documents.filter(doc => 
    doc.document_type === document_type
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">

      <main>
        <RepositoryHeader
          repository={repository as ApiRepository}
          owner={owner}
          repo={repo}
          firstDocumentType={document_type}
        >
          <div className="container mx-auto px-4 py-8 max-w-7xl">
            <Tabs defaultValue={document_type} className="space-y-6">
              <TabsContent value={document_type} className="space-y-6">
                {/* Mobile Responsive Documentation Layout */}
                <div className="">
                  <MobileDocumentationLayout
                    owner={owner}
                    repo={repo}
                    currentDocType={document_type}
                    documents={documents as Tables<'documents'>[]}
                  >
                    <div>
                      {filteredDocuments.length > 0 ? (
                        filteredDocuments.map((doc, index) => (
                          <Card key={index}>
                            <CardHeader>
                              <CardTitle className="text-lg sm:text-xl">{doc.title}</CardTitle>
                              <CardDescription className="text-sm">
                                Generated on {formatDate(doc.created_at)} • {doc.document_type}
                                {doc.generated_by && ` • by ${doc.generated_by}`}
                              </CardDescription>
                            </CardHeader>
                            <CardContent>
                              <div 
                                className="prose dark:prose-invert prose-sm sm:prose-base max-w-none"
                                dangerouslySetInnerHTML={{ __html: marked(doc.content || '') as string }}
                              />
                              {doc.description && (
                                <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                                  <p className="text-sm text-muted-foreground">{doc.description}</p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        ))
                      ) : (
                        <Card>
                          <CardContent className="text-center py-12">
                            <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                            <h3 className="text-base sm:text-lg font-semibold mb-2">No {document_type} Documentation Available</h3>
                            <p className="text-sm sm:text-base text-muted-foreground mb-6">
                              Generate {document_type} documentation for this repository.
                            </p>
                            <GenerateDocsButtons 
                              repositoryId={repository.id} 
                              repositoryName={repository.name} 
                            />
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </MobileDocumentationLayout>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </RepositoryHeader>
      </main>
    </div>
  );
}