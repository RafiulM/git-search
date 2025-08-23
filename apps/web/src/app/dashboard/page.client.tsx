'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';
import { Database, BarChart3, Code, TrendingUp } from 'lucide-react';

interface DashboardClientProps {
  stats: {
    total_repositories?: number;
    total_analyses?: number;
    unique_authors?: number;
    aggregate_metrics?: {
      total_lines?: number;
    };
    processing_stats?: {
      files_processed?: number;
      binary_files_skipped?: number;
      large_files_skipped?: number;
      encoding_errors?: number;
    };
  } | null;
}

export default function DashboardClient({ stats }: DashboardClientProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

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
              <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
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
                      <p className="text-3xl font-bold">{formatNumber(stats.total_repositories || 0)}</p>
                    </div>
                    <Database className="w-8 h-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Analyses</p>
                      <p className="text-3xl font-bold">{formatNumber(stats.total_analyses || 0)}</p>
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
                      <p className="text-3xl font-bold">{formatNumber(stats.aggregate_metrics?.total_lines || 0)}</p>
                    </div>
                    <Code className="w-8 h-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Unique Authors</p>
                      <p className="text-3xl font-bold">{formatNumber(stats.unique_authors || 0)}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-orange-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Processing Stats */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Processing Statistics</CardTitle>
                <CardDescription>
                  Overview of repository analysis processing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Files Processed</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.processing_stats?.files_processed || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Binary Files Skipped</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.processing_stats?.binary_files_skipped || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Large Files Skipped</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.processing_stats?.large_files_skipped || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Encoding Errors</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.processing_stats?.encoding_errors || 0)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Data Available</h3>
              <p className="text-muted-foreground mb-4">
                Start analyzing repositories to see dashboard statistics.
              </p>
              <Link href="/">
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