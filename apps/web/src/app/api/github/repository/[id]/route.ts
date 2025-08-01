import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const supabase = await createSupabaseServerClient();

    const { data: repository, error } = await supabase
      .from('repositories')
      .select(`
        *,
        repository_statistics(*),
        repository_documentation(*),
        repository_files(*)
      `)
      .eq('id', id)
      .single();

    if (error) {
      return NextResponse.json(
        { error: 'Repository not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ repository });
  } catch (error) {
    console.error('Repository fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch repository' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const updates = await request.json();
    const supabase = await createSupabaseServerClient();

    const { data: repository, error } = await supabase
      .from('repositories')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return NextResponse.json(
        { error: 'Failed to update repository' },
        { status: 400 }
      );
    }

    return NextResponse.json({ repository });
  } catch (error) {
    console.error('Repository update error:', error);
    return NextResponse.json(
      { error: 'Failed to update repository' },
      { status: 500 }
    );
  }
}