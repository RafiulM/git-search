import { notFound } from 'next/navigation';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';
import { createSupabaseServerClient } from '@/lib/supabase';
import { GenerateDocsButtons } from '@/components/generate-docs-buttons';
import { MobileDocumentationLayout } from '@/components/mobile-documentation-layout';
import { marked } from 'marked';
import { Tables } from '@/types/database.types';

// Configure marked with GFM support
marked.setOptions({
  gfm: true,
  breaks: true,
});

// Type aliases for better readability
type Repository = Tables<'repositories'>;
type Document = Tables<'documents'>;

interface DocsPageProps {
  params: Promise<{
    owner: string;
    repo: string;
    document_type: string;
  }>;
}

export default async function DocsPage({ params }: DocsPageProps) {
  const { owner, repo, document_type } = await params;
  
  const supabase = await createSupabaseServerClient();
  
  // Construct repo URL from owner and repo parameters
  const repoUrl = `https://github.com/${owner}/${repo}`;
  
  // Fetch repository by repo_url
  const { data: repository, error: repoError } = await supabase
    .from('repositories')
    .select('*')
    .eq('repo_url', repoUrl)
    .single();

  if (repoError || !repository) {
    console.error('Error fetching repository:', repoError);
    notFound();
  }

  // Fetch documents for this repository and document type
  const { data: documents, error: documentsError } = await supabase
    .rpc('get_current_documents', { repo_id: repository.id });

  if (documentsError) {
    console.error('Error fetching documents:', documentsError);
  }

  // Type assertions for function returns
  const typedRepository: Repository = repository;
  const typedDocuments: Document[] = documents || [];
  
  // Filter documents by type
  const filteredDocuments = typedDocuments.filter(doc => 
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
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href={`/repository/${owner}/${repo}`}>
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Back to Repository
                </Button>
              </Link>
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </Link>
            </div>
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main>
        {/* Repository Header */}
        <div className="bg-background border-b">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold mb-2">
                  {typedRepository.name}
                </h1>
                <p className="text-muted-foreground text-sm sm:text-lg">
                  {typedRepository.author ? `by ${typedRepository.author}` : 'Repository'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <Tabs defaultValue="documentation" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <Link href={`/repository/${owner}/${repo}`}>
                <TabsTrigger value="overview" className="w-full">Overview</TabsTrigger>
              </Link>
              <Link href={`/repository/${owner}/${repo}`}>
                <TabsTrigger value="statistics" className="w-full">Statistics</TabsTrigger>
              </Link>
              <Link href={`/repository/${owner}/${repo}`}>
                <TabsTrigger value="files" className="w-full">Files</TabsTrigger>
              </Link>
              <TabsTrigger value="documentation">Documentation</TabsTrigger>
            </TabsList>

            <TabsContent value="documentation" className="space-y-6">
              {/* Mobile Responsive Documentation Layout */}
              <div className="max-w-6xl">
                <MobileDocumentationLayout
                  owner={owner}
                  repo={repo}
                  currentDocType={document_type}
                  documents={typedDocuments}
                >
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-4">
                      <h2 className="text-xl sm:text-2xl font-semibold">{document_type} Documentation</h2>
                      <div className="text-sm text-muted-foreground">
                        ({filteredDocuments.length} document{filteredDocuments.length !== 1 ? 's' : ''})
                      </div>
                    </div>

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
                              dangerouslySetInnerHTML={{ __html: marked(doc.content || '') }}
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
                            repositoryId={typedRepository.id} 
                            repositoryName={typedRepository.name} 
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
      </main>
    </div>
  );
}