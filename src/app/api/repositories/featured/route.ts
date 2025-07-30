import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '4');

    const supabase = await createSupabaseServerClient();

    // Get featured repositories from the repository_summary view which includes analysis data
    const { data: repositories, error } = await supabase
      .from('repository_summary')
      .select('*')
      .not('estimated_tokens', 'is', null)
      .order('favorite_count', { ascending: false })
      .order('estimated_tokens', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Featured repositories error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch featured repositories' },
        { status: 500 }
      );
    }

    // Transform the data to match our expected format
    const featuredRepositories = repositories?.map(repo => ({
      id: repo.id || '',
      name: repo.name || '',
      description: repo.repo_url ? `Repository: ${repo.repo_url}` : null,
      repo_url: repo.repo_url || '',
      author: repo.author,
      branch: repo.branch,
      created_at: repo.created_at || new Date().toISOString(),
      updated_at: repo.updated_at || new Date().toISOString(),
      topics: [], // Could be extracted from analysis_data if available
      language: 'Unknown', // Could be extracted from analysis_data
      stars: 0, // Not available in current schema
      forks: 0, // Not available in current schema
      stats: {
        total_lines: repo.total_lines || 0,
        total_characters: repo.total_characters || 0,
        total_files_found: repo.total_files_found || 0,
        estimated_tokens: repo.estimated_tokens || 0,
        estimated_size_bytes: repo.estimated_size_bytes || 0,
      },
    })) || [];

    return NextResponse.json(featuredRepositories);
  } catch (error) {
    console.error('Featured repositories error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch featured repositories' },
      { status: 500 }
    );
  }
}