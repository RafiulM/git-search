-- Git Search Database Schema
-- This migration creates tables for storing GitHub repository information and analysis

-- Repositories table - stores basic GitHub repo information
CREATE TABLE repositories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  github_id BIGINT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  name TEXT NOT NULL,
  owner_login TEXT NOT NULL,
  description TEXT,
  html_url TEXT NOT NULL,
  clone_url TEXT NOT NULL,
  ssh_url TEXT NOT NULL,
  default_branch TEXT DEFAULT 'main',
  language TEXT,
  languages JSONB DEFAULT '{}',
  topics TEXT[] DEFAULT '{}',
  stars_count INTEGER DEFAULT 0,
  forks_count INTEGER DEFAULT 0,
  watchers_count INTEGER DEFAULT 0,
  open_issues_count INTEGER DEFAULT 0,
  size_kb INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  github_created_at TIMESTAMPTZ,
  github_updated_at TIMESTAMPTZ,
  last_analyzed_at TIMESTAMPTZ,
  is_private BOOLEAN DEFAULT false,
  is_fork BOOLEAN DEFAULT false,
  is_archived BOOLEAN DEFAULT false,
  license_name TEXT,
  has_wiki BOOLEAN DEFAULT false,
  has_pages BOOLEAN DEFAULT false,
  has_downloads BOOLEAN DEFAULT false,
  has_issues BOOLEAN DEFAULT true,
  has_projects BOOLEAN DEFAULT false
);

-- Repository statistics table - stores calculated metrics
CREATE TABLE repository_statistics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
  total_lines INTEGER DEFAULT 0,
  total_characters BIGINT DEFAULT 0,
  file_count INTEGER DEFAULT 0,
  directory_count INTEGER DEFAULT 0,
  estimated_tokens_gpt4 INTEGER DEFAULT 0,
  estimated_tokens_claude3 INTEGER DEFAULT 0,
  estimated_tokens_gemini INTEGER DEFAULT 0,
  storage_size_bytes BIGINT DEFAULT 0,
  language_breakdown JSONB DEFAULT '{}',
  file_type_breakdown JSONB DEFAULT '{}',
  largest_files JSONB DEFAULT '[]',
  complexity_score DECIMAL(5,2) DEFAULT 0,
  maintainability_index DECIMAL(5,2) DEFAULT 0,
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Repository documentation table - stores generated documentation
CREATE TABLE repository_documentation (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
  doc_type TEXT NOT NULL CHECK (doc_type IN ('requirements', 'summary', 'tech_stack', 'frontend_guidelines', 'backend_structure', 'app_flow', 'flowchart')),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  mermaid_diagram TEXT,
  generated_by TEXT DEFAULT 'system',
  generated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  version INTEGER DEFAULT 1,
  is_current BOOLEAN DEFAULT true
);

-- Repository files table - stores file information for analysis
CREATE TABLE repository_files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_extension TEXT,
  file_size_bytes INTEGER DEFAULT 0,
  line_count INTEGER DEFAULT 0,
  character_count INTEGER DEFAULT 0,
  language TEXT,
  is_binary BOOLEAN DEFAULT false,
  last_modified TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(repository_id, file_path)
);

-- User favorites table - stores user's favorite repositories
CREATE TABLE user_favorites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL, -- Clerk user ID
  repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, repository_id)
);

-- Search queries table - stores user search history
CREATE TABLE search_queries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT, -- Clerk user ID (nullable for anonymous searches)
  query TEXT NOT NULL,
  filters JSONB DEFAULT '{}',
  results_count INTEGER DEFAULT 0,
  searched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Repository analysis jobs table - tracks background analysis tasks
CREATE TABLE analysis_jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
  job_type TEXT NOT NULL CHECK (job_type IN ('statistics', 'documentation', 'full_analysis')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  error_message TEXT,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_repositories_full_name ON repositories(full_name);
CREATE INDEX idx_repositories_language ON repositories(language);
CREATE INDEX idx_repositories_stars ON repositories(stars_count DESC);
CREATE INDEX idx_repositories_updated ON repositories(github_updated_at DESC);
CREATE INDEX idx_repositories_owner ON repositories(owner_login);

CREATE INDEX idx_repo_stats_repository_id ON repository_statistics(repository_id);
CREATE INDEX idx_repo_stats_calculated_at ON repository_statistics(calculated_at DESC);

CREATE INDEX idx_repo_docs_repository_id ON repository_documentation(repository_id);
CREATE INDEX idx_repo_docs_type ON repository_documentation(doc_type);
CREATE INDEX idx_repo_docs_current ON repository_documentation(repository_id, doc_type, is_current);

CREATE INDEX idx_repo_files_repository_id ON repository_files(repository_id);
CREATE INDEX idx_repo_files_language ON repository_files(language);
CREATE INDEX idx_repo_files_extension ON repository_files(file_extension);

CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_created ON user_favorites(created_at DESC);

CREATE INDEX idx_search_queries_user_id ON search_queries(user_id);
CREATE INDEX idx_search_queries_searched_at ON search_queries(searched_at DESC);

CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_analysis_jobs_repository_id ON analysis_jobs(repository_id);

-- Enable Row Level Security (RLS)
ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE repository_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE repository_documentation ENABLE ROW LEVEL SECURITY;
ALTER TABLE repository_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_jobs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for repositories (public read, admin write)
CREATE POLICY "Anyone can read repositories" ON repositories
  FOR SELECT USING (true);

CREATE POLICY "Service role can manage repositories" ON repositories
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- RLS Policies for repository_statistics (public read)
CREATE POLICY "Anyone can read repository statistics" ON repository_statistics
  FOR SELECT USING (true);

CREATE POLICY "Service role can manage statistics" ON repository_statistics
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- RLS Policies for repository_documentation (public read)
CREATE POLICY "Anyone can read repository documentation" ON repository_documentation
  FOR SELECT USING (true);

CREATE POLICY "Service role can manage documentation" ON repository_documentation
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- RLS Policies for repository_files (public read)
CREATE POLICY "Anyone can read repository files" ON repository_files
  FOR SELECT USING (true);

CREATE POLICY "Service role can manage files" ON repository_files
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- RLS Policies for user_favorites (user-specific)
CREATE POLICY "Users can manage their own favorites" ON user_favorites
  FOR ALL USING (auth.jwt() ->> 'sub' = user_id);

-- RLS Policies for search_queries (user-specific or anonymous)
CREATE POLICY "Users can read their own search queries" ON search_queries
  FOR SELECT USING (
    auth.jwt() ->> 'sub' = user_id OR 
    user_id IS NULL
  );

CREATE POLICY "Anyone can insert search queries" ON search_queries
  FOR INSERT WITH CHECK (true);

-- RLS Policies for analysis_jobs (public read)
CREATE POLICY "Anyone can read analysis jobs" ON analysis_jobs
  FOR SELECT USING (true);

CREATE POLICY "Service role can manage analysis jobs" ON analysis_jobs
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_repositories_updated_at BEFORE UPDATE ON repositories
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_repository_statistics_updated_at BEFORE UPDATE ON repository_statistics
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_repository_documentation_updated_at BEFORE UPDATE ON repository_documentation
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_jobs_updated_at BEFORE UPDATE ON analysis_jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();