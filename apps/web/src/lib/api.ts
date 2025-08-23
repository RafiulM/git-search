import { RepositoryProcessingStatus, Repository, RepositoryAnalysis, RepositoryWithAnalysis } from './types/api';


export interface PaginatedResponse<T> {
  repositories: T[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    has_more: boolean;
    total_pages: number;
  };
  options: {
    include_analysis: boolean;
  };
}

export interface ListRepositoriesParams {
  skip?: number;
  limit?: number;
  author?: string;
  status?: RepositoryProcessingStatus;
  search?: string;
  include_analysis?: boolean;
  include_ai_summary?: boolean;
}

export interface Document {
  id: string;
  repository_analysis_id: string;
  title: string;
  content: string;
  document_type: string;
  description?: string;
  version: number;
  is_current?: boolean;
  created_at: string;
  updated_at: string;
}

export interface DocumentSummary {
  id: string;
  repository_analysis_id: string;
  title: string;
  document_type: string;
  description?: string;
  version: number;
  is_current?: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedDocumentsResponse {
  documents: Document[] | DocumentSummary[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    has_more: boolean;
    total_pages: number;
  };
  filters: {
    document_type?: string;
    current_only?: boolean;
    summary_only?: boolean;
  };
}

export interface GetRepositoryDocumentsParams {
  skip?: number;
  limit?: number;
  document_type?: string;
  current_only?: boolean;
  summary_only?: boolean;
}

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const API_KEY = process.env.API_KEY || '';

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}/api${endpoint}`;

  console.log(url);
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function listRepositories(params: ListRepositoriesParams = {}): Promise<PaginatedResponse<RepositoryWithAnalysis>> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
  if (params.author) searchParams.append('author', params.author);
  if (params.status) searchParams.append('status', params.status);
  if (params.search) searchParams.append('search', params.search);
  if (params.include_analysis !== undefined) searchParams.append('include_analysis', params.include_analysis.toString());
  if (params.include_ai_summary !== undefined) searchParams.append('include_ai_summary', params.include_ai_summary.toString());

  return apiFetch(`/repositories?${searchParams.toString()}`);
}

export async function getRepository(id: string, include_analysis: boolean = false, include_ai_summary: boolean = false): Promise<Repository | RepositoryAnalysis> {
  const searchParams = new URLSearchParams();
  if (include_analysis) searchParams.append('include_analysis', 'true');
  if (include_ai_summary) searchParams.append('include_ai_summary', 'true');

  return apiFetch(`/repositories/${id}?${searchParams.toString()}`);
}

export async function getRepositoryAnalysis(repoId: string, version?: number): Promise<RepositoryAnalysis> {
  const searchParams = new URLSearchParams();
  if (version !== undefined) searchParams.append('version', version.toString());

  return apiFetch(`/repositories/${repoId}/analysis?${searchParams.toString()}`);
}

export async function getRepositoryOverview(repoId: string): Promise<Repository> {
  return apiFetch(`/repositories/${repoId}/overview`);
}

export async function getRepositoryStatistics(repoId?: string): Promise<{ total_repositories?: number; total_analyses?: number; unique_authors?: number; aggregate_metrics?: { total_lines?: number; }; processing_stats?: { files_processed?: number; binary_files_skipped?: number; large_files_skipped?: number; encoding_errors?: number; }; }> {
  const endpoint = repoId ? `/repositories/${repoId}/stats` : '/repositories/stats';
  return apiFetch(endpoint);
}

export async function getRepositoryDocuments(
  repoId: string,
  params: GetRepositoryDocumentsParams = {}
): Promise<PaginatedDocumentsResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
  if (params.document_type) searchParams.append('document_type', params.document_type);
  if (params.current_only !== undefined) searchParams.append('current_only', params.current_only.toString());
  if (params.summary_only !== undefined) searchParams.append('summary_only', params.summary_only.toString());

  return apiFetch(`/repositories/${repoId}/documents?${searchParams.toString()}`);
}

export async function getRepositoryDocument(repoId: string, documentId: string): Promise<Document> {
  return apiFetch(`/repositories/${repoId}/documents/${documentId}`);
}