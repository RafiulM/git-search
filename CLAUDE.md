# CLAUDE.md - CodeGuide Starter Kit Lite v2

This file contains essential context about the project structure, technologies, and conventions to help Claude understand and work effectively within this codebase.

## Project Overview

**CodeGuide Starter Kit Lite v2** is a modern Next.js starter template featuring authentication, database integration, AI capabilities, and a comprehensive UI component system.

### Core Technologies

- **Framework**: Next.js 15 with App Router (`/src/app` directory structure)
- **Language**: TypeScript with strict mode enabled
- **Styling**: TailwindCSS v4 with CSS custom properties
- **UI Components**: shadcn/ui (New York style) with Lucide icons
- **Authentication**: Clerk with middleware protection
- **Database**: Supabase with third-party auth integration
- **AI Integration**: Vercel AI SDK with support for Anthropic Claude and OpenAI
- **Theme System**: next-themes with dark mode support

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   │   └── chat/          # AI chat endpoint
│   ├── globals.css        # Global styles with dark mode
│   ├── layout.tsx         # Root layout with providers
│   └── page.tsx           # Home page with status dashboard
├── components/
│   ├── ui/                # shadcn/ui components (40+ components)
│   ├── chat.tsx           # AI chat interface
│   ├── setup-guide.tsx    # Configuration guide
│   ├── theme-provider.tsx # Theme context provider
│   └── theme-toggle.tsx   # Dark mode toggle components
├── lib/
│   ├── utils.ts           # Utility functions (cn, etc.)
│   ├── supabase.ts        # Supabase client configurations
│   ├── user.ts            # User utilities using Clerk
│   └── env-check.ts       # Environment validation
└── middleware.ts          # Clerk authentication middleware
```

## Key Configuration Files

- **package.json**: Dependencies and scripts
- **components.json**: shadcn/ui configuration (New York style, neutral colors)
- **tsconfig.json**: TypeScript configuration with path aliases (`@/`)
- **.env.example**: Environment variables template
- **SUPABASE_CLERK_SETUP.md**: Integration setup guide

## Authentication & Database

### Clerk Integration
- Middleware protects `/dashboard(.*)` and `/profile(.*)` routes
- Components: `SignInButton`, `SignedIn`, `SignedOut`, `UserButton`
- User utilities in `src/lib/user.ts` use `currentUser()` from Clerk

### Supabase Integration
- **Client**: `createSupabaseServerClient()` for server-side with Clerk tokens  
- **RLS**: Row Level Security uses `auth.jwt() ->> 'sub'` for Clerk user IDs
- **Example Migration**: `supabase/migrations/001_example_tables_with_rls.sql`

#### Supabase Client Usage Patterns

**Server-side (Recommended for data fetching):**
```typescript
import { createSupabaseServerClient } from "@/lib/supabase"

export async function getServerData() {
  const supabase = await createSupabaseServerClient()
  
  const { data, error } = await supabase
    .from('posts')
    .select('*')
    .order('created_at', { ascending: false })
  
  if (error) {
    console.error('Database error:', error)
    return null
  }
  
  return data
}
```

**Client-side (For interactive operations):**
```typescript
"use client"

import { supabase } from "@/lib/supabase"
import { useAuth } from "@clerk/nextjs"

function ClientComponent() {
  const { getToken } = useAuth()

  const fetchData = async () => {
    const token = await getToken()
    
    // Pass token manually for client-side operations
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .auth(token)
    
    return data
  }
}
```

## UI & Styling

### TailwindCSS Setup
- **Version**: TailwindCSS v4 with PostCSS
- **Custom Properties**: CSS variables for theming
- **Dark Mode**: Class-based with `next-themes`
- **Animations**: `tw-animate-css` package included

### shadcn/ui Components
- **Style**: New York variant
- **Theme**: Neutral base color with CSS variables
- **Icons**: Lucide React
- **Components Available**: 40+ UI components (Button, Card, Dialog, etc.)

### Theme System
- **Provider**: `ThemeProvider` in layout with system detection
- **Toggle Components**: `ThemeToggle` (dropdown) and `SimpleThemeToggle` (button)
- **Persistence**: Automatic theme persistence across sessions

## AI Integration

### Vercel AI SDK
- **Endpoint**: `/api/chat/route.ts`
- **Providers**: Anthropic Claude and OpenAI support
- **Chat Component**: Real-time streaming chat interface
- **Authentication**: Requires Clerk authentication

## Development Conventions

### File Organization
- **Components**: Use PascalCase, place in appropriate directories
- **Utilities**: Place reusable functions in `src/lib/`
- **Types**: Define alongside components or in dedicated files
- **API Routes**: Follow Next.js App Router conventions

### Import Patterns
```typescript
// Path aliases (configured in tsconfig.json)
import { Button } from "@/components/ui/button"
import { getCurrentUser } from "@/lib/user"
import { supabase } from "@/lib/supabase"

// External libraries
import { useTheme } from "next-themes"
import { SignedIn, useAuth } from "@clerk/nextjs"
```

### Component Patterns
```typescript
// Client components (when using hooks/state)
"use client"

// Server components (default, for data fetching)
export default async function ServerComponent() {
  const user = await getCurrentUser()
  // ...
}
```

## Environment Variables

Required for full functionality:

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Supabase Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# AI Integration (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Common Patterns

### Row Level Security (RLS) Policies

All database tables should use RLS policies that reference Clerk user IDs via `auth.jwt() ->> 'sub'`.

**Basic User-Owned Data Pattern:**
```sql
-- Enable RLS on table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can read all posts (public)
CREATE POLICY "Anyone can read posts" ON posts
  FOR SELECT USING (true);

-- Users can only insert posts as themselves
CREATE POLICY "Users can insert own posts" ON posts
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

-- Users can only update their own posts
CREATE POLICY "Users can update own posts" ON posts
  FOR UPDATE USING (auth.jwt() ->> 'sub' = user_id);

-- Users can only delete their own posts
CREATE POLICY "Users can delete own posts" ON posts
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);
```

**Private Data Pattern:**
```sql
-- Completely private to each user
CREATE POLICY "Users can only access own data" ON private_notes
  FOR ALL USING (auth.jwt() ->> 'sub' = user_id);
```

**Conditional Visibility Pattern:**
```sql
-- Public profiles or own profile
CREATE POLICY "Users can read public profiles or own profile" ON profiles
  FOR SELECT USING (
    is_public = true OR auth.jwt() ->> 'sub' = user_id
  );
```

**Collaboration Pattern:**
```sql
-- Owner and collaborators can access
CREATE POLICY "Owners and collaborators can read" ON collaborations
  FOR SELECT USING (
    auth.jwt() ->> 'sub' = owner_id OR 
    auth.jwt() ->> 'sub' = ANY(collaborators)
  );
```

### Database Operations with Supabase

**Complete CRUD Example:**
```typescript
import { createSupabaseServerClient } from "@/lib/supabase"
import { getCurrentUser } from "@/lib/user"

// CREATE - Insert new record
export async function createPost(title: string, content: string) {
  const user = await getCurrentUser()
  if (!user) return null
  
  const supabase = await createSupabaseServerClient()
  
  const { data, error } = await supabase
    .from('posts')
    .insert({
      title,
      content,
      user_id: user.id, // Clerk user ID
    })
    .select()
    .single()
  
  if (error) {
    console.error('Error creating post:', error)
    return null
  }
  
  return data
}

// READ - Fetch user's posts
export async function getUserPosts() {
  const supabase = await createSupabaseServerClient()
  
  const { data, error } = await supabase
    .from('posts')
    .select(`
      id,
      title,
      content,
      created_at,
      user_id
    `)
    .order('created_at', { ascending: false })
  
  if (error) {
    console.error('Error fetching posts:', error)
    return []
  }
  
  return data
}

// UPDATE - Modify existing record
export async function updatePost(postId: string, updates: { title?: string; content?: string }) {
  const supabase = await createSupabaseServerClient()
  
  const { data, error } = await supabase
    .from('posts')
    .update(updates)
    .eq('id', postId)
    .select()
    .single()
  
  if (error) {
    console.error('Error updating post:', error)
    return null
  }
  
  return data
}

// DELETE - Remove record
export async function deletePost(postId: string) {
  const supabase = await createSupabaseServerClient()
  
  const { error } = await supabase
    .from('posts')
    .delete()
    .eq('id', postId)
  
  if (error) {
    console.error('Error deleting post:', error)
    return false
  }
  
  return true
}
```

**Real-time Subscriptions:**
```typescript
"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { useAuth } from "@clerk/nextjs"

function useRealtimePosts() {
  const [posts, setPosts] = useState([])
  const { getToken } = useAuth()

  useEffect(() => {
    const fetchPosts = async () => {
      const token = await getToken()
      
      const { data } = await supabase
        .from('posts')
        .select('*')
        .auth(token)
      
      setPosts(data || [])
    }

    fetchPosts()

    // Subscribe to changes
    const subscription = supabase
      .channel('posts-channel')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'posts' }, 
        (payload) => {
          fetchPosts() // Refetch on any change
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [getToken])

  return posts
}
```

### Protected Routes
Routes matching `/dashboard(.*)` and `/profile(.*)` are automatically protected by Clerk middleware.

### Theme-Aware Components
```typescript
// Automatic dark mode support via CSS custom properties
<div className="bg-background text-foreground border-border">
  <Button variant="outline">Themed Button</Button>
</div>
```

## Development Commands

```bash
npm run dev          # Start development server with Turbopack
npm run build        # Build for production  
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

## Code Quality & Verification

Before committing changes or deploying, ensure code quality by running these checks:

### Quick Verification (Recommended)
```bash
# Run both linting and type checking
npm run lint && npm run type-check
```

### Individual Checks

**ESLint (Code Quality & Style):**
```bash
npm run lint              # Check for linting errors
npm run lint -- --fix    # Auto-fix linting issues where possible
```

**TypeScript Type Checking:**
```bash
npm run type-check        # Verify TypeScript types without emitting files
```

**Production Build (Full Verification):**
```bash
npm run build            # Builds project and performs comprehensive type checking
```

### Pre-Deployment Checklist

Run this complete verification before deploying:

```bash
# 1. Check code style and quality
npm run lint

# 2. Verify TypeScript types
npm run type-check

# 3. Ensure production build works
npm run build

# If all pass, your code is ready for deployment
```

### IDE Integration

For the best development experience, ensure your editor has:
- **ESLint extension** for real-time linting
- **TypeScript support** for type checking
- **TailwindCSS IntelliSense** for styling

### Common Issues & Fixes

**Linting Errors:**
- Use `npm run lint -- --fix` to auto-fix formatting issues
- Check for unused imports, variables, or incorrect patterns
- Ensure consistent coding style

**Type Errors:**
- Verify all imports have correct types
- Check for missing type definitions
- Ensure component props match their interfaces
- Use proper typing for Clerk user objects and Supabase responses

## Best Practices

1. **Authentication**: Always check user state with Clerk hooks/utilities
2. **Database**: Use RLS policies with Clerk user IDs for security
3. **UI**: Leverage existing shadcn/ui components before creating custom ones
4. **Styling**: Use TailwindCSS classes and CSS custom properties for theming
5. **Types**: Maintain strong TypeScript typing throughout
6. **Performance**: Use server components by default, client components only when needed

## Integration Notes

- **Clerk + Supabase**: Uses modern third-party auth (not deprecated JWT templates)
- **AI Chat**: Requires authentication and environment variables
- **Dark Mode**: Automatically applied to all shadcn components
- **Mobile**: Responsive design with TailwindCSS breakpoints

This starter kit provides a solid foundation for building modern web applications with authentication, database integration, AI capabilities, and polished UI components.