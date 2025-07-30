"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  ArrowLeft, 
  Star, 
  GitFork, 
  Eye, 
  Calendar, 
  FileText, 
  BarChart3, 
  Heart,
  ExternalLink,
  Code,
  Zap,
  PieChart,
  Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '@/components/theme-toggle';
// Authentication removed
import MermaidDiagram from '@/components/mermaid-diagram';
import Link from 'next/link';

interface Repository {
  id: string;
  github_id: number;
  full_name: string;
  name: string;
  owner_login: string;
  description: string;
  html_url: string;
  clone_url: string;
  default_branch: string;
  language: string;
  languages: Record<string, number>;
  topics: string[];
  stars_count: number;
  forks_count: number;
  watchers_count: number;
  open_issues_count: number;
  size_kb: number;
  created_at: string;
  updated_at: string;
  github_created_at: string;
  github_updated_at: string;
  last_analyzed_at: string;
  is_private: boolean;
  is_fork: boolean;
  is_archived: boolean;
  license_name: string;
  has_wiki: boolean;
  has_pages: boolean;
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

export default function RepositoryPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  const [generatingDoc, setGeneratingDoc] = useState(false);

  useEffect(() => {
    const fetchRepository = async () => {
      try {
        // Convert slug back to owner/repo format
        const fullName = slug.replace('-', '/');
        
        // For demo purposes, we'll need to find the repo ID first
        // In a real app, you might store the ID in the URL or use a different approach
        const searchResponse = await fetch(`/api/github/search?q=${encodeURIComponent(fullName)}&per_page=1`);
        const searchData = await searchResponse.json();
        
        if (searchData.repositories && searchData.repositories.length > 0) {
          
          // Check if repository is analyzed, if not analyze it
          const analyzeResponse = await fetch('/api/github/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              owner: fullName.split('/')[0], 
              repo: fullName.split('/')[1] 
            }),
          });
          
          if (analyzeResponse.ok) {
            const analyzeData = await analyzeResponse.json();
            
            // Fetch full repository data
            const repoResponse = await fetch(`/api/github/repository/${analyzeData.repository.id}`);
            const repoData = await repoResponse.json();
            
            setRepository(repoData.repository);
          }
        }
      } catch (error) {
        console.error('Error fetching repository:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRepository();
  }, [slug]);

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

  const toggleFavorite = async () => {
    try {
      if (isFavorite) {
        await fetch(`/api/github/favorites?repository_id=${repository?.id}`, {
          method: 'DELETE',
        });
        setIsFavorite(false);
      } else {
        await fetch('/api/github/favorites', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repository_id: repository?.id }),
        });
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const generateDocumentation = async (docType: string) => {
    if (!repository) return;
    
    setGeneratingDoc(true);
    try {
      const response = await fetch('/api/github/documentation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          repository_id: repository.id,
          doc_type: docType 
        }),
      });
      
      if (response.ok) {
        // Refresh repository data to show new documentation
        const fullName = slug.replace('-', '/');
        const searchResponse = await fetch(`/api/github/search?q=${encodeURIComponent(fullName)}&per_page=1`);
        const searchData = await searchResponse.json();
        
        if (searchData.repositories && searchData.repositories.length > 0) {
          const repoResponse = await fetch(`/api/github/repository/${repository.id}`);
          const repoData = await repoResponse.json();
          setRepository(repoData.repository);
        }
      }
    } catch (error) {
      console.error('Error generating documentation:', error);
    } finally {
      setGeneratingDoc(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-8 w-48" />
              <div className="flex items-center gap-4">
                <Skeleton className="h-8 w-8" />
                <Skeleton className="h-8 w-24" />
              </div>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <Skeleton className="h-12 w-96 mb-8" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              {[...Array(3)].map((_, i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-32" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-32 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="space-y-6">
              {[...Array(2)].map((_, i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-24" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-24 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!repository) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-xl font-semibold mb-2">Repository not found</h3>
              <p className="text-muted-foreground mb-4">
                The repository you&apos;re looking for doesn&apos;t exist or hasn&apos;t been analyzed yet.
              </p>
              <Link href="/search">
                <Button>Back to Search</Button>
              </Link>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const stats = repository.repository_statistics[0];
  const languages = stats?.language_breakdown || {};
  const totalLanguageLines = Object.values(languages).reduce((sum, lines) => sum + lines, 0);

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
              <h1 className="text-3xl font-bold mb-2">{repository.full_name}</h1>
              <p className="text-muted-foreground text-lg">
                {repository.description || 'No description available'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <a href={repository.html_url} target="_blank" rel="noopener noreferrer">
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
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="font-medium">{formatNumber(repository.stars_count)}</span>
              <span className="text-muted-foreground">stars</span>
            </div>
            <div className="flex items-center gap-1">
              <GitFork className="w-4 h-4 text-blue-500" />
              <span className="font-medium">{formatNumber(repository.forks_count)}</span>
              <span className="text-muted-foreground">forks</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4 text-green-500" />
              <span className="font-medium">{formatNumber(repository.watchers_count)}</span>
              <span className="text-muted-foreground">watching</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span className="text-muted-foreground">Updated {formatDate(repository.github_updated_at)}</span>
            </div>
          </div>

          {/* Topics */}
          {repository.topics && repository.topics.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {repository.topics.map((topic) => (
                <Badge key={topic} variant="secondary">
                  {topic}
                </Badge>
              ))}
            </div>
          )}
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="files">Files</TabsTrigger>
            <TabsTrigger value="documentation">Documentation</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Stats */}
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Repository Statistics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {stats ? (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {formatNumber(stats.total_lines)}
                          </div>
                          <div className="text-sm text-muted-foreground">Lines of Code</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {stats.file_count}
                          </div>
                          <div className="text-sm text-muted-foreground">Files</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">
                            {formatBytes(stats.storage_size_bytes)}
                          </div>
                          <div className="text-sm text-muted-foreground">Storage</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">
                            {stats.complexity_score.toFixed(1)}
                          </div>
                          <div className="text-sm text-muted-foreground">Complexity</div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-muted-foreground">No statistics available</p>
                    )}
                  </CardContent>
                </Card>

                {/* AI Token Estimates */}
                {stats && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Zap className="w-5 h-5" />
                        AI Model Token Estimates
                      </CardTitle>
                      <CardDescription>
                        Estimated tokens for different AI models
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center p-4 border rounded-lg">
                          <div className="text-xl font-semibold">GPT-4</div>
                          <div className="text-2xl font-bold text-green-600">
                            {formatNumber(stats.estimated_tokens_gpt4)}
                          </div>
                          <div className="text-sm text-muted-foreground">tokens</div>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                          <div className="text-xl font-semibold">Claude 3</div>
                          <div className="text-2xl font-bold text-blue-600">
                            {formatNumber(stats.estimated_tokens_claude3)}
                          </div>
                          <div className="text-sm text-muted-foreground">tokens</div>
                        </div>
                        <div className="text-center p-4 border rounded-lg">
                          <div className="text-xl font-semibold">Gemini</div>
                          <div className="text-2xl font-bold text-purple-600">
                            {formatNumber(stats.estimated_tokens_gemini)}
                          </div>
                          <div className="text-sm text-muted-foreground">tokens</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Repository Info */}
                <Card>
                  <CardHeader>
                    <CardTitle>Repository Info</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Primary Language</span>
                      <span className="font-medium">{repository.language || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">License</span>
                      <span className="font-medium">{repository.license_name || 'None'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Size</span>
                      <span className="font-medium">{repository.size_kb} KB</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Default Branch</span>
                      <span className="font-medium">{repository.default_branch}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Open Issues</span>
                      <span className="font-medium">{repository.open_issues_count}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Language Breakdown */}
                {Object.keys(languages).length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="w-5 h-5" />
                        Languages
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {Object.entries(languages)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 5)
                        .map(([language, lines]) => {
                          const percentage = (lines / totalLanguageLines) * 100;
                          return (
                            <div key={language}>
                              <div className="flex justify-between text-sm mb-1">
                                <span>{language}</span>
                                <span>{percentage.toFixed(1)}%</span>
                              </div>
                              <Progress value={percentage} className="h-2" />
                            </div>
                          );
                        })}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="statistics">
            {stats ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Code Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-2xl font-bold">{formatNumber(stats.total_lines)}</div>
                        <div className="text-sm text-muted-foreground">Total Lines</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{formatNumber(stats.total_characters)}</div>
                        <div className="text-sm text-muted-foreground">Characters</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{stats.file_count}</div>
                        <div className="text-sm text-muted-foreground">Files</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{stats.directory_count}</div>
                        <div className="text-sm text-muted-foreground">Directories</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Quality Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Complexity Score</span>
                        <span className="font-medium">{stats.complexity_score.toFixed(1)}/10</span>
                      </div>
                      <Progress value={stats.complexity_score * 10} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Maintainability Index</span>
                        <span className="font-medium">{stats.maintainability_index.toFixed(1)}/100</span>
                      </div>
                      <Progress value={stats.maintainability_index} className="h-2" />
                    </div>
                  </CardContent>
                </Card>

                {stats.largest_files.length > 0 && (
                  <Card className="lg:col-span-2">
                    <CardHeader>
                      <CardTitle>Largest Files</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {stats.largest_files.map((file, index) => (
                          <div key={index} className="flex justify-between items-center p-2 border rounded">
                            <span className="font-mono text-sm truncate">{file.path}</span>
                            <span className="text-sm text-muted-foreground">{formatBytes(file.size)}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
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
                  <FileText className="w-5 h-5" />
                  Repository Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                {repository.repository_files.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {repository.repository_files
                      .sort((a, b) => b.file_size_bytes - a.file_size_bytes)
                      .map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 border rounded hover:bg-muted/50">
                          <div className="flex items-center gap-2">
                            <Code className="w-4 h-4" />
                            <span className="font-mono text-sm">{file.file_path}</span>
                            {file.language && (
                              <Badge variant="outline" className="text-xs">
                                {file.language}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            {file.line_count > 0 && (
                              <span>{file.line_count} lines</span>
                            )}
                            <span>{formatBytes(file.file_size_bytes)}</span>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No File Data Available</h3>
                    <p className="text-muted-foreground">
                      File analysis is not available for this repository.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documentation">
            <div className="space-y-6">
              {repository.repository_documentation.length > 0 ? (
                repository.repository_documentation.map((doc, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle>{doc.title}</CardTitle>
                      <CardDescription>
                        Generated on {formatDate(doc.generated_at)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="prose dark:prose-invert max-w-none">
                        <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                          {doc.content}
                        </pre>
                      </div>
                      {doc.mermaid_diagram && (
                        <div className="mt-6">
                          <h4 className="font-semibold mb-4">Architecture Diagram</h4>
                          <div className="border rounded-lg p-4 bg-white dark:bg-muted">
                            <MermaidDiagram chart={doc.mermaid_diagram} />
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="text-center py-12">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No Documentation Available</h3>
                    <p className="text-muted-foreground mb-6">
                      Generate comprehensive documentation for this repository.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-2xl mx-auto">
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('summary')}
                      >
                        Summary
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('tech_stack')}
                      >
                        Tech Stack
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('requirements')}
                      >
                        Requirements
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('flowchart')}
                      >
                        Flowchart
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('frontend_guidelines')}
                      >
                        Frontend
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('backend_structure')}
                      >
                        Backend
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        disabled={generatingDoc}
                        onClick={() => generateDocumentation('app_flow')}
                      >
                        App Flow
                      </Button>
                    </div>
                    {generatingDoc && (
                      <p className="text-sm text-muted-foreground mt-4">
                        Generating documentation...
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}