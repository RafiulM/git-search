import { NextRequest, NextResponse } from 'next/server';
import { Octokit } from '@octokit/rest';
import { createSupabaseServerClient } from '@/lib/supabase';

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q');
    const page = parseInt(searchParams.get('page') || '1');
    const per_page = parseInt(searchParams.get('per_page') || '30');
    const sort = searchParams.get('sort') || 'stars';
    const order = searchParams.get('order') || 'desc';

    if (!query) {
      return NextResponse.json(
        { error: 'Search query is required' },
        { status: 400 }
      );
    }

    const response = await octokit.rest.search.repos({
      q: query,
      sort: sort === 'created' ? 'updated' : sort as 'stars' | 'forks' | 'updated',
      order: order as 'asc' | 'desc',
      page,
      per_page,
    });

    const supabase = await createSupabaseServerClient();

    const repositoriesWithStats = await Promise.all(
      response.data.items.map(async (repo) => {
        const { data: existingRepo } = await supabase
          .from('repositories')
          .select(`
            *,
            repository_statistics(*),
            repository_documentation(*)
          `)
          .eq('github_id', repo.id)
          .single();

        if (existingRepo) {
          return {
            ...repo,
            analysis: {
              statistics: existingRepo.repository_statistics,
              documentation: existingRepo.repository_documentation,
              last_analyzed: existingRepo.last_analyzed_at,
            },
          };
        }

        return repo;
      })
    );

    await supabase.from('search_queries').insert({
      query,
      user_id: null, // No user tracking without authentication
      filters: { sort, order, page, per_page },
      results_count: response.data.total_count,
    });

    return NextResponse.json({
      repositories: repositoriesWithStats,
      total_count: response.data.total_count,
      incomplete_results: response.data.incomplete_results,
    });
  } catch (error) {
    console.error('GitHub search error:', error);
    return NextResponse.json(
      { error: 'Failed to search repositories' },
      { status: 500 }
    );
  }
}