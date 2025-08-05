import { NextRequest, NextResponse } from 'next/server';
import { Octokit } from '@octokit/rest';
import { createSupabaseServerClient } from '@/lib/supabase';
import { searchCache, createCacheKey } from '@/lib/cache';
import { searchRateLimiter, getClientIdentifier } from '@/lib/rate-limit';
import { checkEnvironmentVariables } from '@/lib/env-check';
import { searchAnalytics } from '@/lib/analytics';

let octokit: Octokit | null = null;

function getOctokitInstance() {
  if (!octokit) {
    const envStatus = checkEnvironmentVariables();
    
    if (!envStatus.github) {
      throw new Error('GitHub token not configured. Please add GITHUB_TOKEN to your environment variables.');
    }
    
    octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN,
    });
  }
  
  return octokit;
}

interface SearchFilters {
  sort: string;
  order: string;
  page: number;
  per_page: number;
  language?: string;
  topic?: string;
  stars?: string;
  forks?: string;
  created?: string;
  pushed?: string;
}

function buildSearchQuery(baseQuery: string, filters: Partial<SearchFilters>): string {
  let query = baseQuery;
  
  if (filters.language) {
    query += ` language:${filters.language}`;
  }
  
  if (filters.topic) {
    query += ` topic:${filters.topic}`;
  }
  
  if (filters.stars) {
    query += ` stars:${filters.stars}`;
  }
  
  if (filters.forks) {
    query += ` forks:${filters.forks}`;
  }
  
  if (filters.created) {
    query += ` created:${filters.created}`;
  }
  
  if (filters.pushed) {
    query += ` pushed:${filters.pushed}`;
  }
  
  return query.trim();
}

function parseSearchParams(searchParams: URLSearchParams): {
  query: string;
  filters: SearchFilters;
} {
  const query = searchParams.get('q') || '';
  
  const filters: SearchFilters = {
    page: Math.max(1, parseInt(searchParams.get('page') || '1')),
    per_page: Math.min(100, Math.max(1, parseInt(searchParams.get('per_page') || '30'))),
    sort: searchParams.get('sort') || 'stars',
    order: searchParams.get('order') || 'desc',
    language: searchParams.get('language') || undefined,
    topic: searchParams.get('topic') || undefined,
    stars: searchParams.get('stars') || undefined,
    forks: searchParams.get('forks') || undefined,
    created: searchParams.get('created') || undefined,
    pushed: searchParams.get('pushed') || undefined,
  };
  
  return { query, filters };
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  const clientId = getClientIdentifier(request);
  const { searchParams } = new URL(request.url);
  const { query, filters } = parseSearchParams(searchParams);
  
  try {
    if (!searchRateLimiter.isAllowed(clientId)) {
      const resetTime = searchRateLimiter.getResetTime(clientId);
      const remaining = Math.ceil((resetTime - Date.now()) / 1000);
      
      // Track rate limit event
      searchAnalytics.trackRateLimit(query, filters, clientId);
      
      return NextResponse.json(
        { 
          error: 'Rate limit exceeded',
          message: `Too many requests. Please try again in ${remaining} seconds.`,
          retryAfter: remaining,
          suggestions: [
            'Use more specific search terms to get better results',
            'Try searching for specific topics or languages',
            'Consider using advanced search filters'
          ]
        },
        { 
          status: 429,
          headers: {
            'Retry-After': remaining.toString(),
            'X-RateLimit-Limit': '30',
            'X-RateLimit-Remaining': searchRateLimiter.getRemainingRequests(clientId).toString(),
            'X-RateLimit-Reset': Math.ceil(resetTime / 1000).toString(),
          }
        }
      );
    }

    if (!query) {
      return NextResponse.json(
        { 
          error: 'Search query is required',
          message: 'Please provide a search query using the "q" parameter',
          examples: [
            '/api/github/search?q=react',
            '/api/github/search?q=machine+learning&language=python',
            '/api/github/search?q=web+framework&topic=javascript'
          ]
        },
        { status: 400 }
      );
    }

    const cacheKey = createCacheKey(query, filters);
    const cachedResult = searchCache.get(cacheKey) as any;
    
    if (cachedResult) {
      const responseTime = Date.now() - startTime;
      const searchQuery = buildSearchQuery(query, filters);
      
      // Track cached search
      searchAnalytics.trackSearch({
        query: searchQuery,
        filters,
        results_count: cachedResult.total_count || 0,
        response_time_ms: responseTime,
        cached: true,
        client_id: clientId,
      });
      
      return NextResponse.json({
        ...cachedResult,
        meta: {
          cached: true,
          response_time_ms: responseTime,
          rate_limit: {
            remaining: searchRateLimiter.getRemainingRequests(clientId),
            reset_at: searchRateLimiter.getResetTime(clientId),
          }
        }
      });
    }

    const octokitInstance = getOctokitInstance();
    const searchQuery = buildSearchQuery(query, filters);
    
    const validSorts = ['stars', 'forks', 'updated', 'created'] as const;
    const sort = validSorts.includes(filters.sort as typeof validSorts[number]) ? filters.sort as typeof validSorts[number] : 'stars';
    
    const response = await octokitInstance.rest.search.repos({
      q: searchQuery,
      sort: sort === 'created' ? 'updated' : sort,
      order: filters.order as 'asc' | 'desc',
      page: filters.page,
      per_page: filters.per_page,
    });

    const supabase = await createSupabaseServerClient();

    const repositoriesWithStats = await Promise.all(
      response.data.items.map(async (repo) => {
        try {
          const { data: existingRepo } = await supabase
            .from('repositories')
            .select('*')
            .eq('repo_url', `https://github.com/${repo.full_name}`)
            .single();

          if (existingRepo) {
            const { data: analysisData } = await supabase
              .from('repository_analysis')
              .select('*')
              .eq('repository_id', existingRepo.id)
              .single();

            return {
              ...repo,
              analysis: analysisData ? {
                statistics: [analysisData],
                documentation: [],
                last_analyzed: analysisData.updated_at,
              } : undefined,
            };
          }

          return repo;
        } catch (error) {
          console.warn(`Failed to fetch analysis for ${repo.full_name}:`, error);
          return repo;
        }
      })
    );

    const result = {
      repositories: repositoriesWithStats,
      total_count: response.data.total_count,
      incomplete_results: response.data.incomplete_results,
      search_query: searchQuery,
      filters: filters,
    };

    searchCache.set(cacheKey, result, 5 * 60 * 1000); // Cache for 5 minutes

    const responseTime = Date.now() - startTime;

    // Track successful search
    searchAnalytics.trackSearch({
      query: searchQuery,
      filters,
      results_count: response.data.total_count,
      response_time_ms: responseTime,
      cached: false,
      client_id: clientId,
    });

    try {
      const searchLogData = {
        query: searchQuery,
        user_id: null,
        filters: filters,
        results_count: response.data.total_count,
        response_time_ms: responseTime,
        cached: false,
        client_id: clientId,
        timestamp: new Date().toISOString(),
        github_api_remaining: 'unknown', // GitHub API headers not available in Octokit response
        github_api_reset: 'unknown',
      };
      
      console.log('Search performed:', JSON.stringify(searchLogData, null, 2));
      
      // Log cache and rate limit stats periodically
      if (Math.random() < 0.1) { // 10% chance
        console.log('Cache stats:', JSON.stringify(searchCache.getStats(), null, 2));
        console.log('Rate limit stats:', JSON.stringify(searchRateLimiter.getStats(), null, 2));
        console.log('Analytics stats:', JSON.stringify(searchAnalytics.getStats(), null, 2));
      }
    } catch (logError) {
      console.warn('Failed to log search query:', logError);
    }

    return NextResponse.json({
      ...result,
      meta: {
        cached: false,
        response_time_ms: responseTime,
        rate_limit: {
          remaining: searchRateLimiter.getRemainingRequests(clientId),
          reset_at: searchRateLimiter.getResetTime(clientId),
        }
      }
    });

  } catch (error: unknown) {
    console.error('GitHub search error:', error);
    
    const responseTime = Date.now() - startTime;
    
    const err = error as any;
    
    if (err?.status === 403 && err?.message?.includes('rate limit')) {
      searchAnalytics.trackError(query, filters, 'GitHub API rate limit exceeded', clientId);
      
      return NextResponse.json(
        { 
          error: 'GitHub API rate limit exceeded',
          message: 'GitHub API rate limit has been exceeded. Please try again later.',
          suggestions: [
            'Try again in a few minutes',
            'Use more specific search terms',
            'Consider searching during off-peak hours'
          ],
          retryAfter: 60
        },
        { 
          status: 503,
          headers: {
            'Retry-After': '60'
          }
        }
      );
    }
    
    if (err?.status === 422) {
      searchAnalytics.trackError(query, filters, 'Invalid search query', clientId);
      
      return NextResponse.json(
        { 
          error: 'Invalid search query',
          message: 'The search query contains invalid syntax or parameters.',
          suggestions: [
            'Check your search syntax',
            'Avoid special characters in search terms',
            'Use simpler search queries'
          ]
        },
        { status: 400 }
      );
    }

    if (err?.message?.includes('GitHub token not configured')) {
      searchAnalytics.trackError(query, filters, 'GitHub token not configured', clientId);
      
      return NextResponse.json(
        { 
          error: 'Service configuration error',
          message: 'GitHub API is not properly configured. Please contact the administrator.'
        },
        { status: 503 }
      );
    }
    
    searchAnalytics.trackError(query, filters, err?.message || 'Internal server error', clientId);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'An unexpected error occurred while searching repositories.',
        response_time_ms: responseTime
      },
      { status: 500 }
    );
  }
}