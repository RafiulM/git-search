"use client";

// Authentication removed
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  GitBranch,
  BarChart3,
  FileText,
  Zap,
  Database,
  Calendar,
  ExternalLink,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useFeaturedRepositories } from "@/hooks/use-featured-repositories";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const { data: featuredRepositories, isLoading, error } = useFeaturedRepositories(4);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Extract owner/repo from GitHub URL
  const getOwnerRepoFromUrl = (repoUrl: string) => {
    try {
      const url = new URL(repoUrl);
      const pathParts = url.pathname.split('/').filter(Boolean);
      if (pathParts.length >= 2) {
        return `${pathParts[0]}/${pathParts[1]}`;
      }
      return '';
    } catch {
      return '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="text-center py-12 sm:py-16 relative px-4">
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-4">
          <GitBranch className="w-12 h-12 sm:w-16 sm:h-16 text-blue-600" />
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-400 bg-clip-text text-transparent">
            Git Search
          </h1>
        </div>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto px-4 mb-8">
          The ultimate GitHub repository directory with AI-focused statistics and comprehensive analysis
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search repositories (e.g., react typescript, machine learning python)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-base"
              />
            </div>
            <Button type="submit" size="lg" className="h-12 px-8 bg-purple-600 hover:bg-purple-700 text-white">
              Search
            </Button>
          </div>
        </form>

      </div>

      <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-5xl">
        {/* Featured Repositories - Moved to Top */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-2">Featured Repositories</h2>
            <p className="text-muted-foreground">
              Popular repositories with comprehensive AI-focused analysis
            </p>
          </div>
          
          <div className="space-y-4">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 4 }).map((_, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <Skeleton className="h-6 w-2/3" />
                      <Skeleton className="h-4 w-full" />
                      <div className="flex gap-2">
                        <Skeleton className="h-5 w-16" />
                        <Skeleton className="h-5 w-16" />
                        <Skeleton className="h-5 w-16" />
                      </div>
                      <div className="grid grid-cols-4 gap-3 p-3">
                        {Array.from({ length: 4 }).map((_, i) => (
                          <Skeleton key={i} className="h-12 w-full" />
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : error ? (
              // Error state
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">
                    Unable to load featured repositories. Please try again later.
                  </p>
                </CardContent>
              </Card>
            ) : featuredRepositories && featuredRepositories.length > 0 ? (
              // Real data
              featuredRepositories.map((repo) => (
                <Card key={repo.id} className="hover:shadow-lg transition-shadow">
                  <CardContent>
                    <div className="flex-1">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <Link 
                            href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}
                            className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {repo.name}
                          </Link>
                          <a
                            href={repo.repo_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>

                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {formatDate(repo.updated_at)}
                            </div>
                          </div>
                          <Link href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}>
                            <Button variant="outline" size="sm">
                              <BarChart3 className="w-4 h-4 mr-1" />
                              View Analysis
                            </Button>
                          </Link>
                        </div>
                      </div>
                    
                      <p className="text-muted-foreground text-sm mb-2 line-clamp-2">
                        {repo.description || 'No description available'}
                      </p>

                      <div className="flex flex-wrap gap-1 mb-3">
                        {repo.author && (
                          <Badge variant="secondary" className="text-xs">
                            {repo.author}
                          </Badge>
                        )}
                        {repo.branch && (
                          <Badge variant="outline" className="text-xs">
                            {repo.branch}
                          </Badge>
                        )}
                      </div>

                      {/* Statistics with Icons */}
                      <div className="grid grid-cols-4 gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatNumber(repo.stats?.total_lines || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground">Lines</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Database className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatNumber(repo.stats?.total_files_found || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground">Files</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatBytes(repo.stats?.estimated_size_bytes || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground">Size</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Zap className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatNumber(repo.stats?.estimated_tokens || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground">Tokens</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              // No data state
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">
                    No featured repositories available. Start by analyzing some repositories!
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="text-center mt-8">
            <Link href="/search">
              <Button size="lg">
                <Search className="w-4 h-4 mr-2" />
                Explore More Repositories
              </Button>
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mb-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-2">Platform Features</h2>
            <p className="text-muted-foreground">Advanced insights and analysis tools for GitHub repositories</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <Card className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 border-blue-200 dark:border-blue-800">
              <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">Code Statistics</h3>
              <p className="text-sm text-muted-foreground">Lines of code, file counts, and complexity metrics</p>
            </Card>
            
            <Card className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800">
              <Zap className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">AI Token Estimates</h3>
              <p className="text-sm text-muted-foreground">Estimates for GPT-4, Claude, and Gemini models</p>
            </Card>
            
            <Card className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 border-purple-200 dark:border-purple-800">
              <FileText className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">Documentation</h3>
              <p className="text-sm text-muted-foreground">Auto-generated docs and architecture diagrams</p>
            </Card>
            
            <Card className="text-center p-4 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/10 dark:to-red-900/10 border-orange-200 dark:border-orange-800">
              <Database className="w-8 h-8 text-orange-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">Tech Stack Analysis</h3>
              <p className="text-sm text-muted-foreground">Language breakdown and technology insights</p>
            </Card>
          </div>
        </div>

      </main>
    </div>
  );
}
