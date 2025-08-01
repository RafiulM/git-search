import { NextResponse } from 'next/server';

export async function GET() {
  // Authentication disabled - favorites feature not available
  return NextResponse.json(
    { error: 'Favorites feature requires authentication' },
    { status: 401 }
  );
}

export async function POST() {
  // Authentication disabled - favorites feature not available
  return NextResponse.json(
    { error: 'Favorites feature requires authentication' },
    { status: 401 }
  );
}

export async function DELETE() {
  // Authentication disabled - favorites feature not available
  return NextResponse.json(
    { error: 'Favorites feature requires authentication' },
    { status: 401 }
  );
}