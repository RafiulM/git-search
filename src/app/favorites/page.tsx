"use client";

import { useState, useEffect } from 'react';
import { Heart, Star, GitFork, Eye, Calendar, BarChart3, Trash2, ExternalLink, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '@/components/theme-toggle';
import { SignedIn, UserButton } from '@clerk/nextjs';
import Link from 'next/link';

interface Favorite {
  id: string;
  created_at: string;
  repositories: {
    id: string;
    full_name: string;
    name: string;
    description: string;
    html_url: string;
    language: string;
    topics: string[];
    stars_count: number;
    forks_count: number;
    watchers_count: number;
    github_updated_at: string;
    repository_statistics: Array<{
      total_lines: number;
      file_count: number;
      storage_size_bytes: number;
      complexity_score: number;
    }>;
  };
}

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const response = await fetch('/api/github/favorites');
      if (response.ok) {
        const data = await response.json();
        setFavorites(data.favorites || []);
      }
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (repositoryId: string) => {
    try {
      const response = await fetch(`/api/github/favorites?repository_id=${repositoryId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setFavorites(favorites.filter(fav => fav.repositories.id !== repositoryId));
      }
    } catch (error) {
      console.error('Error removing favorite:', error);
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
                  Back to Search
                </Button>
              </Link>
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </Link>
            </div>
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <SignedIn>
                <UserButton />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Heart className="w-8 h-8 text-red-500 fill-current" />
            My Favorites
          </h1>
          <p className="text-muted-foreground">
            Repositories you&apos;ve saved for quick access
          </p>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-6 w-1/3 mb-2" />
                  <Skeleton className="h-4 w-full mb-4" />
                  <div className="flex gap-4">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : favorites.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">💭</div>
              <h3 className="text-xl font-semibold mb-2">No favorites yet</h3>
              <p className="text-muted-foreground mb-4">
                Start exploring repositories and add them to your favorites!
              </p>
              <Link href="/search">
                <Button>
                  Explore Repositories
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {favorites.map((favorite) => {
              const repo = favorite.repositories;
              const stats = repo.repository_statistics[0];
              
              return (
                <Card key={favorite.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Link 
                            href={`/repository/${repo.full_name.replace('/', '-')}`}
                            className="text-xl font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {repo.full_name}
                          </Link>
                          <a
                            href={repo.html_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                        
                        <p className="text-muted-foreground mb-3 line-clamp-2">
                          {repo.description || 'No description available'}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-3">
                          {repo.language && (
                            <Badge variant="secondary">{repo.language}</Badge>
                          )}
                          {repo.topics?.slice(0, 3).map((topic) => (
                            <Badge key={topic} variant="outline">
                              {topic}
                            </Badge>
                          ))}
                          {repo.topics?.length > 3 && (
                            <Badge variant="outline">
                              +{repo.topics.length - 3} more
                            </Badge>
                          )}
                        </div>

                        <div className="flex items-center gap-6 text-sm text-muted-foreground mb-3">
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4" />
                            {formatNumber(repo.stars_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <GitFork className="w-4 h-4" />
                            {formatNumber(repo.forks_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            {formatNumber(repo.watchers_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            Updated {formatDate(repo.github_updated_at)}
                          </div>
                        </div>

                        {stats && (
                          <div className="flex items-center gap-6 text-sm">
                            <div className="flex items-center gap-1 text-blue-600">
                              <BarChart3 className="w-4 h-4" />
                              {formatNumber(stats.total_lines)} lines
                            </div>
                            <div className="text-green-600">
                              {stats.file_count} files
                            </div>
                            <div className="text-purple-600">
                              {formatBytes(stats.storage_size_bytes)}
                            </div>
                            <div className="text-orange-600">
                              Complexity: {stats.complexity_score.toFixed(1)}
                            </div>
                          </div>
                        )}

                        <div className="text-xs text-muted-foreground mt-2">
                          Added to favorites on {formatDate(favorite.created_at)}
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 ml-4">
                        <Link href={`/repository/${repo.full_name.replace('/', '-')}`}>
                          <Button variant="outline" size="sm">
                            <BarChart3 className="w-4 h-4 mr-1" />
                            View Details
                          </Button>
                        </Link>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeFavorite(repo.id)}
                          className="text-red-600 hover:text-red-800 hover:border-red-300"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Remove
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}