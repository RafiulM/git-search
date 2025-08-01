-- Example migration showing RLS implementation for Clerk + Supabase integration
-- This creates sample tables with proper RLS policies based on Clerk user IDs

-- Create a posts table as an example
CREATE TABLE IF NOT EXISTS public.posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  user_id TEXT NOT NULL, -- This will store the Clerk user ID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create a comments table as another example
CREATE TABLE IF NOT EXISTS public.comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES public.posts(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  user_id TEXT NOT NULL, -- This will store the Clerk user ID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create a profiles table for user-specific data
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT UNIQUE NOT NULL, -- This will store the Clerk user ID
  bio TEXT,
  website TEXT,
  avatar_url TEXT,
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security on all tables
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for posts table
-- Users can read all posts (public access)
CREATE POLICY "Anyone can read posts" ON public.posts
  FOR SELECT USING (true);

-- Users can only insert posts as themselves
CREATE POLICY "Users can insert own posts" ON public.posts
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

-- Users can only update their own posts
CREATE POLICY "Users can update own posts" ON public.posts
  FOR UPDATE USING (auth.jwt() ->> 'sub' = user_id);

-- Users can only delete their own posts
CREATE POLICY "Users can delete own posts" ON public.posts
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);

-- RLS Policies for comments table
-- Users can read all comments (public access)
CREATE POLICY "Anyone can read comments" ON public.comments
  FOR SELECT USING (true);

-- Users can only insert comments as themselves
CREATE POLICY "Users can insert own comments" ON public.comments
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

-- Users can only update their own comments
CREATE POLICY "Users can update own comments" ON public.comments
  FOR UPDATE USING (auth.jwt() ->> 'sub' = user_id);

-- Users can only delete their own comments
CREATE POLICY "Users can delete own comments" ON public.comments
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);

-- RLS Policies for profiles table
-- Users can read public profiles or their own profile
CREATE POLICY "Users can read public profiles or own profile" ON public.profiles
  FOR SELECT USING (
    is_public = true OR auth.jwt() ->> 'sub' = user_id
  );

-- Users can only insert their own profile
CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.jwt() ->> 'sub' = user_id);

-- Users can only delete their own profile
CREATE POLICY "Users can delete own profile" ON public.profiles
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON public.posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON public.posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON public.comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON public.comments(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_posts_updated_at
  BEFORE UPDATE ON public.posts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at
  BEFORE UPDATE ON public.comments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Example of more complex RLS policy with additional conditions
-- Create a private_notes table that's completely private to each user
CREATE TABLE IF NOT EXISTS public.private_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  user_id TEXT NOT NULL, -- This will store the Clerk user ID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.private_notes ENABLE ROW LEVEL SECURITY;

-- Private notes can only be accessed by the owner
CREATE POLICY "Users can only access own private notes" ON public.private_notes
  FOR ALL USING (auth.jwt() ->> 'sub' = user_id);

-- Example of collaborative table with shared access
CREATE TABLE IF NOT EXISTS public.collaborations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  owner_id TEXT NOT NULL, -- Clerk user ID of the owner
  collaborators TEXT[] DEFAULT '{}', -- Array of Clerk user IDs
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.collaborations ENABLE ROW LEVEL SECURITY;

-- Owners and collaborators can read
CREATE POLICY "Owners and collaborators can read collaborations" ON public.collaborations
  FOR SELECT USING (
    auth.jwt() ->> 'sub' = owner_id OR 
    auth.jwt() ->> 'sub' = ANY(collaborators)
  );

-- Only owners can insert
CREATE POLICY "Owners can insert collaborations" ON public.collaborations
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = owner_id);

-- Only owners can update
CREATE POLICY "Owners can update collaborations" ON public.collaborations
  FOR UPDATE USING (auth.jwt() ->> 'sub' = owner_id);

-- Only owners can delete
CREATE POLICY "Owners can delete collaborations" ON public.collaborations
  FOR DELETE USING (auth.jwt() ->> 'sub' = owner_id);

CREATE INDEX IF NOT EXISTS idx_collaborations_owner_id ON public.collaborations(owner_id);
CREATE INDEX IF NOT EXISTS idx_collaborations_collaborators ON public.collaborations USING GIN(collaborators);

CREATE TRIGGER update_collaborations_updated_at
  BEFORE UPDATE ON public.collaborations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();