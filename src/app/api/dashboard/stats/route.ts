import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();

    // Get total repositories count
    const { count: totalRepositories } = await supabase
      .from('repositories')
      .select('*', { count: 'exact', head: true });

    // Get analyzed repositories count
    const { count: totalAnalyzed } = await supabase
      .from('repositories')
      .select('*', { count: 'exact', head: true })
      .not('last_analyzed_at', 'is', null);

    // Get aggregate statistics
    const { data: statsData } = await supabase
      .from('repository_statistics')
      .select(`
        total_lines,
        file_count,
        complexity_score,
        repository_id,
        repositories!inner(language)
      `);

    let totalLines = 0;
    let totalFiles = 0;
    let totalComplexity = 0;
    const languageCounts: Record<string, number> = {};

    if (statsData) {
      statsData.forEach(stat => {
        totalLines += stat.total_lines || 0;
        totalFiles += stat.file_count || 0;
        totalComplexity += stat.complexity_score || 0;
        
        const language = (stat.repositories as { language?: string })?.language;
        if (language) {
          languageCounts[language] = (languageCounts[language] || 0) + 1;
        }
      });
    }

    const averageComplexity = statsData && statsData.length > 0 
      ? totalComplexity / statsData.length 
      : 0;

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
        full_name,
        stars_count,
        language,
        last_analyzed_at
      `)
      .not('last_analyzed_at', 'is', null)
      .order('last_analyzed_at', { ascending: false })
      .limit(10);

    const formattedRecentAnalyses = recentAnalyses?.map(repo => ({
      repository: {
        full_name: repo.full_name,
        stars_count: repo.stars_count,
        language: repo.language,
      },
      analyzed_at: repo.last_analyzed_at,
    })) || [];

    const dashboardStats = {
      totalRepositories: totalRepositories || 0,
      totalAnalyzed: totalAnalyzed || 0,
      totalLines,
      totalFiles,
      averageComplexity,
      topLanguages,
      recentAnalyses: formattedRecentAnalyses,
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