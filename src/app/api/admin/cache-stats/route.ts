import { NextRequest, NextResponse } from 'next/server';
import { searchCache } from '@/lib/cache';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const detailed = searchParams.get('detailed') === 'true';
    
    const stats = detailed ? searchCache.getDetailedStats() : searchCache.getStats();
    
    return NextResponse.json({
      cache: stats,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Cache stats error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve cache statistics' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const key = searchParams.get('key');
    
    if (key) {
      // Delete specific cache entry
      const deleted = searchCache.delete(key);
      return NextResponse.json({ 
        deleted, 
        key,
        message: deleted ? 'Cache entry deleted' : 'Cache entry not found'
      });
    } else {
      // Clear entire cache
      searchCache.clear();
      return NextResponse.json({ 
        message: 'Cache cleared successfully' 
      });
    }
  } catch (error) {
    console.error('Cache management error:', error);
    return NextResponse.json(
      { error: 'Failed to manage cache' },
      { status: 500 }
    );
  }
}