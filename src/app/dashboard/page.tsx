"use client";

import { BarChart3, TrendingUp, Code, Database, Star, Activity, Calendar } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '@/components/theme-toggle';
// Authentication removed
import Link from 'next/link';
import { useDashboardStats } from '@/hooks/use-dashboard-stats';

export default function DashboardPage() {
  const { data: stats, isLoading: loading, error } = useDashboardStats();

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
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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
                <Skeleton className="h-8 w-8" />
              </div>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <Skeleton className="h-10 w-64 mb-8" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-16 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </Link>
              <Badge variant="secondary">Dashboard</Badge>
            </div>
            
            <div className="flex items-center gap-4">
              <Link href="/search" className="text-sm text-muted-foreground hover:text-foreground">
                Search
              </Link>
              <Link href="/favorites" className="text-sm text-muted-foreground hover:text-foreground">
                Favorites
              </Link>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Repository Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive insights across analyzed repositories
          </p>
        </div>

        {stats ? (
          <>
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Repositories</p>
                      <p className="text-3xl font-bold">{formatNumber(stats.totalRepositories)}</p>
                    </div>
                    <Database className="w-8 h-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Analyzed</p>
                      <p className="text-3xl font-bold">{formatNumber(stats.totalAnalyzed)}</p>
                      <p className="text-xs text-muted-foreground">
                        {stats.totalRepositories > 0 
                          ? Math.round((stats.totalAnalyzed / stats.totalRepositories) * 100) 
                          : 0}% coverage
                      </p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Lines</p>
                      <p className="text-3xl font-bold">{formatNumber(stats.totalLines)}</p>
                    </div>
                    <Code className="w-8 h-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Avg Complexity</p>
                      <p className="text-3xl font-bold">{stats.averageComplexity.toFixed(1)}</p>
                      <p className="text-xs text-muted-foreground">out of 10</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-orange-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Language Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Language Distribution</CardTitle>
                  <CardDescription>
                    Most popular programming languages in analyzed repositories
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {stats.topLanguages.slice(0, 8).map((lang, index) => (
                      <div key={lang.language}>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="font-medium">{lang.language}</span>
                          <span className="text-muted-foreground">
                            {lang.count} repos ({lang.percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <Progress value={lang.percentage} className="h-2" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Analyses */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Analyses</CardTitle>
                  <CardDescription>
                    Latest repository analyses and their details
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {stats.recentAnalyses.slice(0, 6).map((analysis, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50">
                        <div className="flex-1">
                          <Link 
                            href={`/repository/${analysis.repository.full_name.replace('/', '-')}`}
                            className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {analysis.repository.full_name}
                          </Link>
                          <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Star className="w-3 h-3" />
                              {formatNumber(analysis.repository.stars_count)}
                            </div>
                            {analysis.repository.language && (
                              <Badge variant="outline" className="text-xs">
                                {analysis.repository.language}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(analysis.analyzed_at)}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Additional Stats */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Code Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total Files</span>
                      <span className="font-medium">{formatNumber(stats.totalFiles)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Avg Files/Repo</span>
                      <span className="font-medium">
                        {stats.totalAnalyzed > 0 
                          ? Math.round(stats.totalFiles / stats.totalAnalyzed) 
                          : 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Avg Lines/Repo</span>
                      <span className="font-medium">
                        {stats.totalAnalyzed > 0 
                          ? formatNumber(Math.round(stats.totalLines / stats.totalAnalyzed))
                          : 0}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quality Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-muted-foreground">Avg Complexity</span>
                        <span className="font-medium">{stats.averageComplexity.toFixed(1)}/10</span>
                      </div>
                      <Progress value={stats.averageComplexity * 10} className="h-2" />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Lower complexity indicates better maintainability
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Analysis Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-muted-foreground">Repositories Analyzed</span>
                        <span className="font-medium">
                          {stats.totalAnalyzed}/{stats.totalRepositories}
                        </span>
                      </div>
                      <Progress 
                        value={stats.totalRepositories > 0 
                          ? (stats.totalAnalyzed / stats.totalRepositories) * 100 
                          : 0} 
                        className="h-2" 
                      />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {stats.totalRepositories - stats.totalAnalyzed} repositories pending analysis
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <Activity className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Data Available</h3>
              <p className="text-muted-foreground mb-4">
                Start analyzing repositories to see dashboard statistics.
              </p>
              <Link href="/search">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Search Repositories
                </button>
              </Link>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}