-- Repository Relations Refactor Migration
-- This migration creates a cleaner separation between repositories, statistics, and documents
-- Following the user's specific requirements for table structure

-- Create the main repositories table with basic repo information
CREATE TABLE IF NOT EXISTS public.repositories (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- Repository identification
  name TEXT NOT NULL,
  repo_url TEXT NOT NULL UNIQUE,
  author TEXT NULL,
  branch TEXT NULL,
  
  -- Content storage
  full_text TEXT NULL,
  full_text_path TEXT NULL,
  content_url TEXT NULL,
  content_expires_at TIMESTAMP WITH TIME ZONE NULL,
  
  CONSTRAINT repositories_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;

-- Create repository_analysis table for tracking analysis data over time
CREATE TABLE IF NOT EXISTS public.repository_analysis (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  repository_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- File processing stats
  files_processed INTEGER NULL,
  binary_files_skipped INTEGER NULL,
  large_files_skipped INTEGER NULL,
  encoding_errors INTEGER NULL,
  
  -- Content metrics
  total_characters INTEGER NULL,
  total_lines INTEGER NULL,
  total_files_found INTEGER NULL,
  total_directories INTEGER NULL,
  
  -- Size estimates
  estimated_tokens INTEGER NULL,
  estimated_size_bytes INTEGER NULL,
  
  -- Tree structure from repository analysis
  tree_structure TEXT NULL,
  
  -- Additional analysis data as JSON for flexibility
  analysis_data JSONB NULL,
  
  -- Analysis version for tracking changes over time
  analysis_version INTEGER NOT NULL DEFAULT 1,
  
  CONSTRAINT repository_analysis_pkey PRIMARY KEY (id),
  CONSTRAINT repository_analysis_repository_id_fkey FOREIGN KEY (repository_id) 
    REFERENCES public.repositories(id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Create documents table for generated documentation
CREATE TABLE IF NOT EXISTS public.documents (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  repository_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- Document metadata
  document_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NULL,
  
  -- Document content
  content TEXT NOT NULL,
  
  -- Generation metadata
  generated_by TEXT NULL DEFAULT 'system',
  generation_prompt TEXT NULL,
  model_used TEXT NULL,
  
  -- Version control
  version INTEGER NOT NULL DEFAULT 1,
  is_current BOOLEAN DEFAULT true,
  parent_document_id UUID NULL,
  
  -- Additional metadata as JSON
  metadata JSONB NULL DEFAULT '{}',
  
  CONSTRAINT documents_pkey PRIMARY KEY (id),
  CONSTRAINT documents_repository_id_fkey FOREIGN KEY (repository_id) 
    REFERENCES public.repositories(id) ON DELETE CASCADE,
  CONSTRAINT documents_parent_document_id_fkey FOREIGN KEY (parent_document_id) 
    REFERENCES public.documents(id) ON DELETE SET NULL
) TABLESPACE pg_default;

-- Create user_favorites table for users to favorite repositories
CREATE TABLE IF NOT EXISTS public.user_favorites (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL, -- Clerk user ID
  repository_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  CONSTRAINT user_favorites_pkey PRIMARY KEY (id),
  CONSTRAINT user_favorites_repository_id_fkey FOREIGN KEY (repository_id) 
    REFERENCES public.repositories(id) ON DELETE CASCADE,
  -- Ensure each user can only favorite a repository once
  CONSTRAINT user_favorites_unique UNIQUE (user_id, repository_id)
) TABLESPACE pg_default;

-- Enable Row Level Security on all tables
ALTER TABLE public.repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.repository_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_favorites ENABLE ROW LEVEL SECURITY;

-- RLS Policies for repositories table - public read only, write via service_role_key only
CREATE POLICY "Anyone can read repositories" ON public.repositories
  FOR SELECT USING (true);

-- RLS Policies for repository_analysis table - public read only, write via service_role_key only
CREATE POLICY "Anyone can read repository analysis" ON public.repository_analysis
  FOR SELECT USING (true);

-- RLS Policies for documents table - anyone can read/write
CREATE POLICY "Anyone can read documents" ON public.documents
  FOR SELECT USING (true);

-- RLS Policies for user_favorites table
-- Anyone can read favorites (for public discovery)
CREATE POLICY "Anyone can read user favorites" ON public.user_favorites
  FOR SELECT USING (true);

-- Users can only manage their own favorites
CREATE POLICY "Users can insert own favorites" ON public.user_favorites
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

CREATE POLICY "Users can delete own favorites" ON public.user_favorites
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_repositories_created_at ON public.repositories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_repositories_author ON public.repositories(author);

CREATE INDEX IF NOT EXISTS idx_repository_analysis_repository_id ON public.repository_analysis(repository_id);
CREATE INDEX IF NOT EXISTS idx_repository_analysis_created_at ON public.repository_analysis(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_repository_analysis_version ON public.repository_analysis(repository_id, analysis_version DESC);

CREATE INDEX IF NOT EXISTS idx_documents_repository_id ON public.documents(repository_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON public.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_current ON public.documents(repository_id, document_type, is_current);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON public.documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_version ON public.documents(repository_id, document_type, version DESC);

CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON public.user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_repository_id ON public.user_favorites(repository_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_created_at ON public.user_favorites(created_at DESC);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_repositories_updated_at
  BEFORE UPDATE ON public.repositories
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_repository_analysis_updated_at
  BEFORE UPDATE ON public.repository_analysis
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
  BEFORE UPDATE ON public.documents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically mark old documents as not current when inserting new versions
CREATE OR REPLACE FUNCTION handle_document_versioning()
RETURNS TRIGGER AS $$
BEGIN
  -- If this is marked as current, mark all other documents of the same type as not current
  IF NEW.is_current = true THEN
    UPDATE public.documents 
    SET is_current = false 
    WHERE repository_id = NEW.repository_id 
      AND document_type = NEW.document_type 
      AND id != NEW.id;
  END IF;
  
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER handle_document_versioning_trigger
  AFTER INSERT ON public.documents
  FOR EACH ROW
  EXECUTE FUNCTION handle_document_versioning();

-- Create function to get latest analysis for a repository
CREATE OR REPLACE FUNCTION get_latest_repository_analysis(repo_id UUID)
RETURNS public.repository_analysis AS $$
DECLARE
  latest_analysis public.repository_analysis;
BEGIN
  SELECT * INTO latest_analysis
  FROM public.repository_analysis
  WHERE repository_id = repo_id
  ORDER BY created_at DESC
  LIMIT 1;
  
  RETURN latest_analysis;
END;
$$ language 'plpgsql';

-- Create function to get current documents for a repository
CREATE OR REPLACE FUNCTION get_current_documents(repo_id UUID)
RETURNS SETOF public.documents AS $$
BEGIN
  RETURN QUERY
  SELECT *
  FROM public.documents
  WHERE repository_id = repo_id
    AND is_current = true
  ORDER BY document_type, created_at DESC;
END;
$$ language 'plpgsql';

-- Create function to check if a user has favorited a repository
CREATE OR REPLACE FUNCTION is_favorited_by_user(repo_id UUID, user_id_param TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  is_favorited BOOLEAN;
BEGIN
  SELECT EXISTS(
    SELECT 1 
    FROM public.user_favorites 
    WHERE repository_id = repo_id 
      AND user_id = user_id_param
  ) INTO is_favorited;
  
  RETURN is_favorited;
END;
$$ language 'plpgsql';

-- Create function to get user's favorite repositories
CREATE OR REPLACE FUNCTION get_user_favorite_repositories(user_id_param TEXT)
RETURNS SETOF public.repositories AS $$
BEGIN
  RETURN QUERY
  SELECT r.*
  FROM public.repositories r
  INNER JOIN public.user_favorites uf ON r.id = uf.repository_id
  WHERE uf.user_id = user_id_param
  ORDER BY uf.created_at DESC;
END;
$$ language 'plpgsql';

-- Create view for repository summary with latest analysis and favorite count
CREATE OR REPLACE VIEW repository_summary AS
SELECT 
  r.id,
  r.name,
  r.repo_url,
  r.author,
  r.branch,
  r.created_at,
  r.updated_at,
  ra.files_processed,
  ra.total_characters,
  ra.total_lines,
  ra.total_files_found,
  ra.total_directories,
  ra.estimated_tokens,
  ra.estimated_size_bytes,
  ra.tree_structure,
  ra.analysis_data,
  ra.created_at as analysis_created_at,
  COALESCE(fav_count.favorite_count, 0) as favorite_count
FROM public.repositories r
LEFT JOIN LATERAL (
  SELECT *
  FROM public.repository_analysis
  WHERE repository_id = r.id
  ORDER BY created_at DESC
  LIMIT 1
) ra ON true
LEFT JOIN (
  SELECT 
    repository_id,
    COUNT(*) as favorite_count
  FROM public.user_favorites
  GROUP BY repository_id
) fav_count ON r.id = fav_count.repository_id;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.repositories TO anon, authenticated;
GRANT SELECT ON public.repository_analysis TO anon, authenticated;
GRANT SELECT ON public.documents TO anon, authenticated;
GRANT SELECT ON public.user_favorites TO anon, authenticated;
GRANT SELECT ON public.repository_summary TO anon, authenticated;

-- repositories and repository_analysis are only writable via service_role_key
GRANT INSERT, UPDATE, DELETE ON public.documents TO authenticated;
GRANT INSERT, DELETE ON public.user_favorites TO authenticated;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;