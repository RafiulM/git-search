import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';

export async function GET() {
  try {
    const supabase = await createSupabaseServerClient();
    
    // Get all favorited repositories with their details
    const { data: favorites, error } = await supabase
      .from('repository_summary')
      .select(`
        id,
        name,
        repo_url,
        author,
        branch,
        created_at,
        updated_at,
        files_processed,
        total_files_found,
        total_lines,
        estimated_tokens,
        favorite_count,
        analysis_created_at
      `)
      .gt('favorite_count', 0)
      .order('favorite_count', { ascending: false });

    if (error) {
      console.error('Error fetching favorites:', error);
      return NextResponse.json(
        { error: 'Failed to fetch favorites' },
        { status: 500 }
      );
    }

    return NextResponse.json(favorites || []);
  } catch (error) {
    console.error('Error in favorites API:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { repository_id, user_id = 'anonymous' } = body;

    if (!repository_id) {
      return NextResponse.json(
        { error: 'Repository ID is required' },
        { status: 400 }
      );
    }

    const supabase = await createSupabaseServerClient();
    
    // Check if already favorited
    const { data: existing } = await supabase
      .from('user_favorites')
      .select('id')
      .eq('repository_id', repository_id)
      .eq('user_id', user_id)
      .single();

    if (existing) {
      return NextResponse.json(
        { error: 'Repository already favorited' },
        { status: 409 }
      );
    }

    // Add to favorites
    const { data, error } = await supabase
      .from('user_favorites')
      .insert({
        repository_id,
        user_id
      })
      .select()
      .single();

    if (error) {
      console.error('Error adding favorite:', error);
      return NextResponse.json(
        { error: 'Failed to add favorite' },
        { status: 500 }
      );
    }

    return NextResponse.json({ 
      message: 'Repository favorited successfully',
      favorite: data
    });
  } catch (error) {
    console.error('Error in favorites POST:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const url = new URL(request.url);
    const repository_id = url.searchParams.get('repository_id');
    const user_id = url.searchParams.get('user_id') || 'anonymous';

    if (!repository_id) {
      return NextResponse.json(
        { error: 'Repository ID is required' },
        { status: 400 }
      );
    }

    const supabase = await createSupabaseServerClient();
    
    const { error } = await supabase
      .from('user_favorites')
      .delete()
      .eq('repository_id', repository_id)
      .eq('user_id', user_id);

    if (error) {
      console.error('Error removing favorite:', error);
      return NextResponse.json(
        { error: 'Failed to remove favorite' },
        { status: 500 }
      );
    }

    return NextResponse.json({ 
      message: 'Repository unfavorited successfully'
    });
  } catch (error) {
    console.error('Error in favorites DELETE:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}