import { NextRequest, NextResponse } from 'next/server';
import { searchAnalytics } from '@/lib/analytics';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const timeRange = searchParams.get('timeRange');
    const query = searchParams.get('query');
    const action = searchParams.get('action');
    
    // Handle different actions
    if (action === 'recent') {
      const limit = parseInt(searchParams.get('limit') || '50');
      const recentSearches = searchAnalytics.getRecentSearches(limit);
      return NextResponse.json({
        recentSearches,
        count: recentSearches.length,
        timestamp: new Date().toISOString(),
      });
    }
    
    if (action === 'history' && query) {
      const limit = parseInt(searchParams.get('limit') || '10');
      const searchHistory = searchAnalytics.getSearchHistory(query, limit);
      return NextResponse.json({
        query,
        searchHistory,
        count: searchHistory.length,
        timestamp: new Date().toISOString(),
      });
    }
    
    // Default: get analytics stats
    let timeRangeMs: number | undefined;
    
    switch (timeRange) {
      case '1h':
        timeRangeMs = 60 * 60 * 1000;
        break;
      case '24h':
        timeRangeMs = 24 * 60 * 60 * 1000;
        break;
      case '7d':
        timeRangeMs = 7 * 24 * 60 * 60 * 1000;
        break;
      case '30d':
        timeRangeMs = 30 * 24 * 60 * 60 * 1000;
        break;
      default:
        timeRangeMs = undefined; // All time
    }
    
    const stats = searchAnalytics.getStats(timeRangeMs);
    
    return NextResponse.json({
      analytics: stats,
      timeRange: timeRange || 'all',
      timeRangeMs,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Search analytics error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve search analytics' },
      { status: 500 }
    );
  }
}