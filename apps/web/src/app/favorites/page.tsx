"use client";

import { useState } from 'react';
import { Heart, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ThemeToggle } from '@/components/theme-toggle';
import { ViewToggle } from '@/components/view-toggle';
import { useFavorites } from '@/hooks/use-favorites';
import Link from 'next/link';

interface FavoriteRepository {
  id: string;
  name: string;
  repo_url: string;
  author: string | null;
  branch: string | null;
  created_at: string;
  updated_at: string;
  files_processed: number | null;
  total_files_found: number | null;
  total_lines: number | null;
  estimated_tokens: number | null;
  favorite_count: number;
  analysis_created_at: string | null;
}

function FavoriteCards({ repositories, viewMode }: { repositories: FavoriteRepository[], viewMode: "list" | "grid" }) {
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

  if (viewMode === "grid") {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {repositories.map((repo) => (
          <Card key={repo.id} className="hover:shadow-lg transition-all duration-200 hover:scale-[1.02]">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-3">
                <Link 
                  href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}
                  className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 line-clamp-1"
                >
                  {repo.name}
                </Link>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-red-500">
                    <Heart className="w-4 h-4 fill-current" />
                    <span className="text-xs font-medium">{repo.favorite_count}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-1 mb-4">
                {repo.author && (
                  <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
                    {repo.author}
                  </span>
                )}
                {repo.branch && (
                  <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs rounded border">
                    {repo.branch}
                  </span>
                )}
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-semibold text-blue-600">
                    {formatNumber(repo.total_lines || 0)}
                  </div>
                  <div className="text-xs text-muted-foreground">Lines</div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-semibold text-green-600">
                    {formatNumber(repo.total_files_found || 0)}
                  </div>
                  <div className="text-xs text-muted-foreground">Files</div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground">
                  {formatDate(repo.created_at)}
                </div>
                <Link href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}>
                  <Button variant="outline" size="sm" className="text-xs">
                    View Details
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // List view
  return (
    <div className="space-y-4">
      {repositories.map((repo) => (
        <Card key={repo.id} className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Link 
                    href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}
                    className="text-xl font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    {repo.name}
                  </Link>
                  <div className="flex items-center gap-1 text-red-500">
                    <Heart className="w-4 h-4 fill-current" />
                    <span className="text-sm font-medium">{repo.favorite_count}</span>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {repo.author && (
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
                      {repo.author}
                    </span>
                  )}
                  {repo.branch && (
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs rounded border">
                      {repo.branch}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="text-sm text-muted-foreground">
                  {formatDate(repo.created_at)}
                </div>
                <Link href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </Link>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded">
              <div className="text-center">
                <div className="text-lg font-semibold text-blue-600">
                  {formatNumber(repo.total_lines || 0)}
                </div>
                <div className="text-xs text-muted-foreground">Lines</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-green-600">
                  {formatNumber(repo.total_files_found || 0)}
                </div>
                <div className="text-xs text-muted-foreground">Files</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-purple-600">
                  {formatNumber(repo.estimated_tokens || 0)}
                </div>
                <div className="text-xs text-muted-foreground">Tokens</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-orange-600">
                  {formatNumber(repo.files_processed || 0)}
                </div>
                <div className="text-xs text-muted-foreground">Processed</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function FavoritesPage() {
  const [viewMode, setViewMode] = useState<"list" | "grid">("grid");
  const { data: favorites, isLoading, error } = useFavorites();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Back to Search
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

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
                <Heart className="w-8 h-8 text-red-500 fill-current" />
                Favorited Repositories
              </h1>
              <p className="text-muted-foreground">
                {isLoading ? 'Loading favorites...' : `${favorites?.length || 0} repositories have been favorited by users`}
              </p>
            </div>
            
            {favorites && favorites.length > 0 && (
              <ViewToggle viewMode={viewMode} onViewModeChange={setViewMode} />
            )}
          </div>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="ml-2">Loading favorites...</span>
          </div>
        )}

        {error && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-xl font-semibold mb-2">Error Loading Favorites</h3>
              <p className="text-muted-foreground mb-4">
                There was an error loading the favorite repositories. Please try again later.
              </p>
              <Button onClick={() => window.location.reload()}>
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && favorites && favorites.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">💭</div>
              <h3 className="text-xl font-semibold mb-2">No Favorites Yet</h3>
              <p className="text-muted-foreground mb-4">
                No repositories have been favorited yet. Start exploring and favoriting repositories!
              </p>
              <Link href="/">
                <Button>
                  Start Searching
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && favorites && favorites.length > 0 && (
          <FavoriteCards repositories={favorites} viewMode={viewMode} />
        )}
      </main>
    </div>
  );
}