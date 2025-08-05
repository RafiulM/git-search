"use client";

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { GitBranch } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';
import { EnhancedSearch } from '@/components/enhanced-search';
import { SearchResults } from '@/components/search-results';
import Link from 'next/link';
import { useRepositorySearch } from '@/hooks/use-repository-search';
import { useRepositoryAnalysis } from '@/hooks/use-repository-analysis';

interface Repository {
  id: number;
  full_name: string;
  name: string;
  description: string;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  watchers_count: number;
  language: string;
  topics: string[];
  updated_at: string;
  size: number;
  analysis?: {
    statistics: unknown[];
    documentation: unknown[];
    last_analyzed: string;
  };
}

interface SearchFilters {
  sort: string;
  order: string;
  language?: string;
  topic?: string;
  stars?: string;
  forks?: string;
  created?: string;
  pushed?: string;
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [filters, setFilters] = useState<SearchFilters>({
    sort: searchParams.get('sort') || 'stars',
    order: searchParams.get('order') || 'desc',
    language: searchParams.get('language') || undefined,
    topic: searchParams.get('topic') || undefined,
    stars: searchParams.get('stars') || undefined,
    forks: searchParams.get('forks') || undefined,
    created: searchParams.get('created') || undefined,
    pushed: searchParams.get('pushed') || undefined,
  });
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1'));

  const { data: searchResults, isLoading: loading, error } = useRepositorySearch({
    query,
    ...filters,
    page,
    per_page: 30,
  });

  const { mutate: analyzeRepository, isPending: isAnalyzing } = useRepositoryAnalysis();

  useEffect(() => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (filters.sort !== 'stars') params.set('sort', filters.sort);
    if (filters.order !== 'desc') params.set('order', filters.order);
    if (filters.language) params.set('language', filters.language);
    if (filters.topic) params.set('topic', filters.topic);
    if (filters.stars) params.set('stars', filters.stars);
    if (filters.forks) params.set('forks', filters.forks);
    if (filters.created) params.set('created', filters.created);
    if (filters.pushed) params.set('pushed', filters.pushed);
    if (page !== 1) params.set('page', page.toString());

    const newUrl = `/search${params.toString() ? `?${params.toString()}` : ''}`;
    router.replace(newUrl, { scroll: false });
  }, [query, filters, page, router]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q && q !== query) {
      setQuery(q);
      setPage(1);
    }
  }, [searchParams, query]);

  const handleSearch = () => {
    setPage(1);
  };

  const handleAnalyzeRepository = (repo: Repository) => {
    const [owner, name] = repo.full_name.split('/');
    analyzeRepository({ owner, repo: name });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <GitBranch className="w-8 h-8 text-blue-600" />
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </div>
            </Link>
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Enhanced Search Component */}
        <EnhancedSearch
          query={query}
          onQueryChange={setQuery}
          filters={filters}
          onFiltersChange={setFilters}
          onSearch={handleSearch}
          isLoading={loading}
          error={error}
          className="mb-8"
        />

        {/* Enhanced Search Results Component */}
        <SearchResults
          data={searchResults}
          isLoading={loading}
          error={error}
          page={page}
          onPageChange={setPage}
          perPage={30}
          onAnalyzeRepository={handleAnalyzeRepository}
          isAnalyzing={isAnalyzing}
        />
      </main>
    </div>
  );
}