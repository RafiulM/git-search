// Processing Status Types
export type RepositoryProcessingStatus = 
  | 'pending'
  | 'queued'
  | 'processing'
  | 'analyzed'
  | 'docs_generated'
  | 'completed'
  | 'failed';

// API Response Types

export interface Document {
  id: string;
  repository_analysis_id: string;
  title: string;
  content: string;
  document_type: string;
  description: string | null;
  version: number;
  is_current: boolean;
  created_at: string;
  updated_at?: string;
  generated_by?: string;
}

export interface RepositoryAnalysis {
  id: string;
  repository_id: string;
  analysis_version: number;
  total_files_found: number;
  total_directories: number;
  files_processed: number;
  total_lines: number;
  total_characters: number;
  estimated_tokens: number;
  estimated_size_bytes: number;
  large_files_skipped: number;
  binary_files_skipped: number;
  encoding_errors: number;
  tree_structure?: string;
  readme_image_src?: string;
  ai_summary?: string | null;
  description?: string;
  forked_repo_url?: string | null;
  twitter_link?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface Repository {
  id: string;
  name: string;
  repo_url: string;
  author: string;
  branch?: string | null;
  twitter_link?: string | null;
  processing_status: RepositoryProcessingStatus;
  created_at: string;
  updated_at: string;
  full_text?: string | null;
  analysis?: RepositoryAnalysis | null;
}

export interface RepositoryWithAnalysis extends Repository {
  analysis?: RepositoryAnalysis | null;
}

export interface Pagination {
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
  total_pages: number;
}

export interface DocumentsFilters {
  document_type?: string | null;
  current_only?: boolean;
  summary_only?: boolean;
}

export interface RepositoriesOptions {
  include_analysis?: boolean;
  include_ai_summary?: boolean;
  search?: string;
  limit?: number;
}

// API Response Interfaces
export interface DocumentsResponse {
  documents: Document[];
  pagination: Pagination;
  filters: DocumentsFilters;
}

export interface RepositoriesResponse {
  repositories: Repository[];
  pagination: Pagination;
  options: RepositoriesOptions;
}

// API Function Parameter Types
export interface GetRepositoryDocumentsParams {
  document_type?: string;
  current_only?: boolean;
  summary_only?: boolean;
}

export interface ListRepositoriesParams {
  search?: string;
  include_analysis?: boolean;
  include_ai_summary?: boolean;
  limit?: number;
  page?: number;
}