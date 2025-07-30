-- Repository Relations Refactor Migration
-- This migration creates a cleaner separation between repositories, statistics, and documents
-- Following the user's specific requirements for table structure

-- Create the main repositories table with basic repo information
CREATE TABLE IF NOT EXISTS public.repositories (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- Repository identification
  name TEXT NULL,
  repo_url TEXT NULL,
  author TEXT NULL,
  branch TEXT NULL,
  
  -- Content storage
  full_text TEXT NULL,
  tree_structure TEXT NULL,
  full_text_path TEXT NULL,
  content_url TEXT NULL,
  content_expires_at TIMESTAMP WITH TIME ZONE NULL,
  
  -- Analysis metadata
  analysis_version INTEGER NULL DEFAULT 1,
  
  -- User ownership (for RLS)
  user_id TEXT NOT NULL, -- Clerk user ID
  
  CONSTRAINT repositories_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;

-- Create repository_stats table for tracking statistics over time
CREATE TABLE IF NOT EXISTS public.repository_stats (
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
  
  -- Additional statistics as JSON for flexibility
  statistics JSONB NULL,
  
  -- Stats version for tracking changes over time
  stats_version INTEGER NOT NULL DEFAULT 1,
  
  CONSTRAINT repository_stats_pkey PRIMARY KEY (id),
  CONSTRAINT repository_stats_repository_id_fkey FOREIGN KEY (repository_id) 
    REFERENCES public.repositories(id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Create documents table for generated documentation
CREATE TABLE IF NOT EXISTS public.documents (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  repository_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  -- Document metadata
  document_type TEXT NOT NULL CHECK (document_type IN (
    'project_requirements',
    'tech_stack',
    'summary',
    'app_flow',
    'backend_structure',
    'frontend_guidelines',
    'security_guidelines',
    'api_documentation',
    'setup_guide',
    'flowchart',
    'mermaid_diagram'
  )),
  title TEXT NOT NULL,
  description TEXT NULL,
  
  -- Document content
  content TEXT NOT NULL,
  content_format TEXT NOT NULL DEFAULT 'markdown' CHECK (content_format IN ('markdown', 'html', 'json', 'mermaid')),
  
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

-- Enable Row Level Security on all tables
ALTER TABLE public.repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.repository_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies for repositories table
-- Users can read all repositories (public access for discovery)
CREATE POLICY "Anyone can read repositories" ON public.repositories
  FOR SELECT USING (true);

-- Users can only insert repositories as themselves
CREATE POLICY "Users can insert own repositories" ON public.repositories
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);

-- Users can only update their own repositories
CREATE POLICY "Users can update own repositories" ON public.repositories
  FOR UPDATE USING (auth.jwt() ->> 'sub' = user_id);

-- Users can only delete their own repositories
CREATE POLICY "Users can delete own repositories" ON public.repositories
  FOR DELETE USING (auth.jwt() ->> 'sub' = user_id);

-- RLS Policies for repository_stats table
-- Users can read all repository stats (public access)
CREATE POLICY "Anyone can read repository stats" ON public.repository_stats
  FOR SELECT USING (true);

-- Users can insert stats for repositories they own
CREATE POLICY "Users can insert stats for own repositories" ON public.repository_stats
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = repository_stats.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- Users can update stats for repositories they own
CREATE POLICY "Users can update stats for own repositories" ON public.repository_stats
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = repository_stats.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- Users can delete stats for repositories they own
CREATE POLICY "Users can delete stats for own repositories" ON public.repository_stats
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = repository_stats.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- RLS Policies for documents table
-- Users can read all documents (public access for sharing)
CREATE POLICY "Anyone can read documents" ON public.documents
  FOR SELECT USING (true);

-- Users can insert documents for repositories they own
CREATE POLICY "Users can insert documents for own repositories" ON public.documents
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = documents.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- Users can update documents for repositories they own
CREATE POLICY "Users can update documents for own repositories" ON public.documents
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = documents.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- Users can delete documents for repositories they own
CREATE POLICY "Users can delete documents for own repositories" ON public.documents
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.repositories 
      WHERE repositories.id = documents.repository_id 
      AND repositories.user_id = auth.jwt() ->> 'sub'
    )
  );

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_repositories_user_id ON public.repositories(user_id);
CREATE INDEX IF NOT EXISTS idx_repositories_created_at ON public.repositories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_repositories_repo_url ON public.repositories(repo_url);
CREATE INDEX IF NOT EXISTS idx_repositories_author ON public.repositories(author);

CREATE INDEX IF NOT EXISTS idx_repository_stats_repository_id ON public.repository_stats(repository_id);
CREATE INDEX IF NOT EXISTS idx_repository_stats_created_at ON public.repository_stats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_repository_stats_stats_version ON public.repository_stats(repository_id, stats_version DESC);

CREATE INDEX IF NOT EXISTS idx_documents_repository_id ON public.documents(repository_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON public.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_current ON public.documents(repository_id, document_type, is_current);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON public.documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_version ON public.documents(repository_id, document_type, version DESC);

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

CREATE TRIGGER update_repository_stats_updated_at
  BEFORE UPDATE ON public.repository_stats
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

-- Create function to get latest stats for a repository
CREATE OR REPLACE FUNCTION get_latest_repository_stats(repo_id UUID)
RETURNS public.repository_stats AS $$
DECLARE
  latest_stats public.repository_stats;
BEGIN
  SELECT * INTO latest_stats
  FROM public.repository_stats
  WHERE repository_id = repo_id
  ORDER BY created_at DESC
  LIMIT 1;
  
  RETURN latest_stats;
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

-- Create view for repository summary with latest stats
CREATE OR REPLACE VIEW repository_summary AS
SELECT 
  r.id,
  r.name,
  r.repo_url,
  r.author,
  r.branch,
  r.created_at,
  r.updated_at,
  r.user_id,
  rs.files_processed,
  rs.total_characters,
  rs.total_lines,
  rs.total_files_found,
  rs.total_directories,
  rs.estimated_tokens,
  rs.estimated_size_bytes,
  rs.statistics,
  rs.created_at as stats_created_at
FROM public.repositories r
LEFT JOIN LATERAL (
  SELECT *
  FROM public.repository_stats
  WHERE repository_id = r.id
  ORDER BY created_at DESC
  LIMIT 1
) rs ON true;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.repositories TO anon, authenticated;
GRANT SELECT ON public.repository_stats TO anon, authenticated;
GRANT SELECT ON public.documents TO anon, authenticated;
GRANT SELECT ON public.repository_summary TO anon, authenticated;

GRANT INSERT, UPDATE, DELETE ON public.repositories TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.repository_stats TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.documents TO authenticated;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;