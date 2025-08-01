import { notFound } from 'next/navigation';
import { 
  ArrowLeft, 
  Calendar, 
  BarChart3, 
  ExternalLink,
  Code,
  Zap,
  Activity,
  CodeIcon,
  FileIcon,
  HardDrive,
  FolderIcon,
  AlertTriangle,
  Settings,
  Hash,
  Database
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';
import { createSupabaseServerClient } from '@/lib/supabase';
import { RepositoryTree } from '@/components/repository-tree';
import { DocumentationTab } from '@/components/documentation-tab';
import { Tables } from '@/types/database.types';

// Type aliases for better readability
type Repository = Tables<'repositories'>;
type RepositoryAnalysis = Tables<'repository_analysis'>;
type Document = Tables<'documents'>;

interface RepositoryPageProps {
  params: Promise<{
    owner: string;
    repo: string;
  }>;
}

export default async function RepositoryPage({ params }: RepositoryPageProps) {
  const { owner, repo } = await params;
  
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

  // Fetch latest analysis using the database function
  const { data: analysis, error: analysisError } = await supabase
    .rpc('get_latest_repository_analysis', { repo_id: repository.id });

  if (analysisError) {
    console.error('Error fetching analysis:', analysisError);
  }

  // Fetch current documents using the database function
  const { data: documents, error: documentsError } = await supabase
    .rpc('get_current_documents', { repo_id: repository.id });

  if (documentsError) {
    console.error('Error fetching documents:', documentsError);
  }

  // Type assertions for function returns (since RPC functions don't have perfect type inference)
  const typedRepository: Repository = repository;
  const typedAnalysis: RepositoryAnalysis | null = analysis;
  const typedDocuments: Document[] = documents || [];

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

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
              <Link href="/search">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Back
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

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Repository Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">{typedRepository.name}</h1>
              <p className="text-muted-foreground text-lg">
                {typedRepository.author ? `by ${typedRepository.author}` : 'Repository'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <a href={typedRepository.repo_url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm">
                  <ExternalLink className="w-4 h-4 mr-1" />
                  View on GitHub
                </Button>
              </a>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span className="text-muted-foreground">Created {formatDate(typedRepository.created_at)}</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span className="text-muted-foreground">Updated {formatDate(typedRepository.updated_at)}</span>
            </div>
            {typedRepository.branch && (
              <div className="flex items-center gap-1">
                <Code className="w-4 h-4" />
                <span className="text-muted-foreground">Branch: {typedRepository.branch}</span>
              </div>
            )}
          </div>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="files">Files</TabsTrigger>
            <TabsTrigger value="documentation">Documentation</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Key Repository Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Key Statistics
                </CardTitle>
                <CardDescription>
                  Essential metrics for this repository
                </CardDescription>
              </CardHeader>
              <CardContent>
                {typedAnalysis ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                      <CodeIcon className="w-8 h-8 text-blue-600" />
                      <div>
                        <div className="text-2xl font-bold text-blue-600">
                          {typedAnalysis.total_lines ? formatNumber(typedAnalysis.total_lines) : 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Lines of Code</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                      <FileIcon className="w-8 h-8 text-green-600" />
                      <div>
                        <div className="text-2xl font-bold text-green-600">
                          {typedAnalysis.total_files_found || 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Files</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                      <HardDrive className="w-8 h-8 text-purple-600" />
                      <div>
                        <div className="text-2xl font-bold text-purple-600">
                          {typedAnalysis.estimated_size_bytes ? formatBytes(typedAnalysis.estimated_size_bytes) : 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Storage</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                      <FolderIcon className="w-8 h-8 text-cyan-600" />
                      <div>
                        <div className="text-2xl font-bold text-cyan-600">
                          {typedAnalysis.total_directories || 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">Directories</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No analysis data available</p>
                )}
              </CardContent>
            </Card>

            {/* Repository Info */}
            <Card>
              <CardHeader>
                <CardTitle>Repository Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Repository URL</span>
                  <span className="font-medium text-sm">{typedRepository.repo_url}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Author</span>
                  <span className="font-medium">{typedRepository.author || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Branch</span>
                  <span className="font-medium">{typedRepository.branch || 'main'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created</span>
                  <span className="font-medium">{formatDate(typedRepository.created_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Updated</span>
                  <span className="font-medium">{formatDate(typedRepository.updated_at)}</span>
                </div>
                {typedAnalysis && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Analyzed</span>
                    <span className="font-medium">{formatDate(typedAnalysis.created_at)}</span>
                  </div>
                )}
              </CardContent>
            </Card>

          </TabsContent>

          <TabsContent value="statistics">
            {typedAnalysis ? (
              <div className="space-y-6">
                {/* Comprehensive Code Metrics */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Comprehensive Code Metrics
                    </CardTitle>
                    <CardDescription>
                      Detailed statistics and analysis data
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <CodeIcon className="w-8 h-8 text-blue-600" />
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {typedAnalysis.total_lines ? formatNumber(typedAnalysis.total_lines) : 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Total Lines</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <Hash className="w-8 h-8 text-green-600" />
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {typedAnalysis.total_characters ? formatNumber(typedAnalysis.total_characters) : 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Characters</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <FileIcon className="w-8 h-8 text-purple-600" />
                        <div>
                          <div className="text-2xl font-bold text-purple-600">
                            {typedAnalysis.total_files_found || 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Files Found</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <Settings className="w-8 h-8 text-orange-600" />
                        <div>
                          <div className="text-2xl font-bold text-orange-600">
                            {typedAnalysis.files_processed || 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Files Processed</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <FolderIcon className="w-8 h-8 text-cyan-600" />
                        <div>
                          <div className="text-2xl font-bold text-cyan-600">
                            {typedAnalysis.total_directories || 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Directories</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <HardDrive className="w-8 h-8 text-indigo-600" />
                        <div>
                          <div className="text-2xl font-bold text-indigo-600">
                            {typedAnalysis.estimated_size_bytes ? formatBytes(typedAnalysis.estimated_size_bytes) : 'N/A'}
                          </div>
                          <div className="text-sm text-muted-foreground">Storage Size</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* AI Token Estimates */}
                {typedAnalysis.estimated_tokens && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Zap className="w-5 h-5" />
                        AI Token Estimates
                      </CardTitle>
                      <CardDescription>
                        Estimated tokens for AI processing and analysis
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3 p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                        <Zap className="w-12 h-12 text-blue-600" />
                        <div>
                          <div className="text-3xl font-bold text-blue-600">
                            {formatNumber(typedAnalysis.estimated_tokens)}
                          </div>
                          <div className="text-lg text-muted-foreground">Estimated Tokens</div>
                          <div className="text-sm text-muted-foreground">For AI model processing</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Analysis Details */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="w-5 h-5" />
                      Analysis Details
                    </CardTitle>
                    <CardDescription>
                      Processing details and analysis metadata
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-yellow-600" />
                            <span className="text-muted-foreground">Binary Files Skipped</span>
                          </div>
                          <span className="font-medium">{typedAnalysis.binary_files_skipped || '0'}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-orange-600" />
                            <span className="text-muted-foreground">Large Files Skipped</span>
                          </div>
                          <span className="font-medium">{typedAnalysis.large_files_skipped || '0'}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                            <span className="text-muted-foreground">Encoding Errors</span>
                          </div>
                          <span className="font-medium">{typedAnalysis.encoding_errors || '0'}</span>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <Settings className="w-5 h-5 text-blue-600" />
                            <span className="text-muted-foreground">Analysis Version</span>
                          </div>
                          <span className="font-medium">{typedAnalysis.analysis_version}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-purple-600" />
                            <span className="text-muted-foreground">Analyzed On</span>
                          </div>
                          <span className="font-medium">{formatDate(typedAnalysis.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">No Statistics Available</h3>
                  <p className="text-muted-foreground">
                    This repository hasn&apos;t been analyzed yet.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="files">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderIcon className="w-5 h-5" />
                  Repository File Structure
                </CardTitle>
                <CardDescription>
                  Explore the repository files and folders with an interactive tree view
                </CardDescription>
              </CardHeader>
              <CardContent>
                {typedAnalysis && typedAnalysis.tree_structure ? (
                  <RepositoryTree treeString={typedAnalysis.tree_structure} />
                ) : (
                  <div className="text-center py-12">
                    <FolderIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No File Structure Available</h3>
                    <p className="text-muted-foreground">
                      File structure analysis is not available for this repository.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documentation">
            <DocumentationTab 
              documents={typedDocuments} 
              owner={owner} 
              repo={repo} 
            />
          </TabsContent>

        </Tabs>
      </main>
    </div>
  );
}