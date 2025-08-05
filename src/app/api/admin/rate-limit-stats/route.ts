import { NextRequest, NextResponse } from 'next/server';
import { searchRateLimiter, getClientIdentifier } from '@/lib/rate-limit';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const detailed = searchParams.get('detailed') === 'true';
    const clientId = searchParams.get('client');
    
    if (clientId) {
      // Get stats for specific client
      const clientInfo = searchRateLimiter.getClientInfo(clientId);
      return NextResponse.json({
        client: clientInfo,
        timestamp: new Date().toISOString(),
      });
    }
    
    const stats = detailed ? searchRateLimiter.getDetailedStats() : searchRateLimiter.getStats();
    
    return NextResponse.json({
      rateLimiting: stats,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Rate limit stats error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve rate limit statistics' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, clientId, additionalRequests, durationMs } = body;
    
    if (action === 'reset' && clientId) {
      const reset = searchRateLimiter.resetClient(clientId);
      return NextResponse.json({
        success: reset,
        message: reset ? 'Client rate limit reset' : 'Client not found',
        clientId,
      });
    }
    
    if (action === 'increase' && clientId && additionalRequests) {
      searchRateLimiter.increaseLimit(clientId, additionalRequests, durationMs);
      return NextResponse.json({
        success: true,
        message: `Increased limit for client by ${additionalRequests} requests`,
        clientId,
        additionalRequests,
        durationMs: durationMs || 'default',
      });
    }
    
    return NextResponse.json(
      { error: 'Invalid action or missing parameters' },
      { status: 400 }
    );
  } catch (error) {
    console.error('Rate limit management error:', error);
    return NextResponse.json(
      { error: 'Failed to manage rate limits' },
      { status: 500 }
    );
  }
}