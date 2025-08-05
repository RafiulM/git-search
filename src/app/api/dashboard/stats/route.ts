import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';
import { searchAnalytics } from '@/lib/analytics';
import { searchCache } from '@/lib/cache';
import { searchRateLimiter } from '@/lib/rate-limit';

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();

    // Get total repositories count
    const { count: totalRepositories } = await supabase
      .from('repositories')
      .select('*', { count: 'exact', head: true });

    // Get analyzed repositories count using repository_analysis table
    const { count: totalAnalyzed } = await supabase
      .from('repository_analysis')
      .select('*', { count: 'exact', head: true });

    // Get aggregate statistics from repository_analysis table
    const { data: statsData } = await supabase
      .from('repository_analysis')
      .select(`
        total_lines,
        files_processed,
        repository_id
      `);

    let totalLines = 0;
    let totalFiles = 0;
    const languageCounts: Record<string, number> = {};

    if (statsData) {
      statsData.forEach(stat => {
        totalLines += stat.total_lines || 0;
        totalFiles += stat.files_processed || 0;
      });
    }

    // Get language distribution from repositories
    const { data: repositories } = await supabase
      .from('repositories')
      .select('author');

    if (repositories) {
      repositories.forEach(repo => {
        const language = repo.author || 'Unknown'; // Using author as proxy since language field doesn't exist
        languageCounts[language] = (languageCounts[language] || 0) + 1;
      });
    }

    const averageComplexity = 0; // Not available in current schema

    // Calculate language percentages
    const totalReposWithLanguage = Object.values(languageCounts).reduce((sum, count) => sum + count, 0);
    const topLanguages = Object.entries(languageCounts)
      .map(([language, count]) => ({
        language,
        count,
        percentage: totalReposWithLanguage > 0 ? (count / totalReposWithLanguage) * 100 : 0,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Get recent analyses
    const { data: recentAnalyses } = await supabase
      .from('repositories')
      .select(`
        name,
        author,
        updated_at
      `)
      .order('updated_at', { ascending: false })
      .limit(10);

    const formattedRecentAnalyses = recentAnalyses?.map(repo => ({
      repository: {
        full_name: repo.name,
        stars_count: 0, // Not available in current schema
        language: repo.author || 'Unknown',
      },
      analyzed_at: repo.updated_at,
    })) || [];

    // Get search analytics (last 24 hours)
    const searchStats = searchAnalytics.getStats(24 * 60 * 60 * 1000);
    const cacheStats = searchCache.getStats();
    const rateLimitStats = searchRateLimiter.getStats();
    const recentSearches = searchAnalytics.getRecentSearches(5);

    const dashboardStats = {
      totalRepositories: totalRepositories || 0,
      totalAnalyzed: totalAnalyzed || 0,
      totalLines,
      totalFiles,
      averageComplexity,
      topLanguages,
      recentAnalyses: formattedRecentAnalyses,
      searchAnalytics: {
        totalSearches24h: searchStats.totalSearches,
        uniqueQueries24h: searchStats.uniqueQueries,
        averageResponseTime: searchStats.averageResponseTime,
        cacheHitRate: searchStats.cacheHitRate,
        errorRate: searchStats.errorRate,
        rateLimitRate: searchStats.rateLimitRate,
        topQueries: searchStats.topQueries.slice(0, 5), // Top 5
        topFilters: searchStats.topFilters.slice(0, 5), // Top 5
        recentSearches: recentSearches.map(search => ({
          query: search.query,
          results_count: search.results_count,
          response_time_ms: search.response_time_ms,
          cached: search.cached,
          timestamp: new Date(search.timestamp).toISOString(),
          error: search.error,
        })),
      },
      systemStats: {
        cache: {
          size: cacheStats.size,
          hitRate: cacheStats.hitRate,
          memoryUsage: cacheStats.totalMemoryUsage,
        },
        rateLimiting: {
          activeClients: rateLimitStats.activeClients,
          totalBlocked: rateLimitStats.totalBlocked,
          blockRate: rateLimitStats.blockRate,
        },
      },
    };

    return NextResponse.json(dashboardStats);
  } catch (error) {
    console.error('Dashboard stats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard statistics' },
      { status: 500 }
    );
  }
}