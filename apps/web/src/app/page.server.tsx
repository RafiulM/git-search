import { GitBranch } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';
import HomeClient from './page.client';
import { SearchForm } from '@/components/search-form';
import { FeaturedRepositoriesServer } from '@/components/featured-repositories-server';
import { SearchResultsServer } from '@/components/search-results-server';

// ISR Configuration - Cache featured repositories for 30 minutes
export const revalidate = 1800;

interface HomePageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = await searchParams;
  const searchQuery = typeof params.q === 'string' ? params.q : '';
  const sort = typeof params.sort === 'string' ? params.sort : 'stars';
  const order = typeof params.order === 'string' ? params.order : 'desc';
  const page = typeof params.page === 'string' ? parseInt(params.page) : 1;
  const viewMode = typeof params.view === 'string' && (params.view === 'list' || params.view === 'grid') ? params.view : 'grid';
  
  const isSearchMode = searchQuery.trim().length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="text-center py-12 sm:py-16 relative px-4">
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <Link href="/favorites" className="text-sm text-muted-foreground hover:text-foreground px-3 py-2 rounded-md hover:bg-muted transition-colors">
              Favorites
            </Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground px-3 py-2 rounded-md hover:bg-muted transition-colors">
              Dashboard
            </Link>
            <ThemeToggle />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-4">
          <GitBranch className="w-12 h-12 sm:w-16 sm:h-16 text-blue-600" />
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-400 bg-clip-text text-transparent">
            Git Search
          </h1>
        </div>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto px-4 mb-8">
          The ultimate GitHub repository directory with AI-focused statistics and comprehensive analysis
        </p>

        {/* Search Form */}
        <SearchForm initialQuery={searchQuery} />
      </div>

      <HomeClient 
        searchQuery={searchQuery}
        sort={sort}
        order={order}
        page={page}
        viewMode={viewMode}
        isSearchMode={isSearchMode}
      >
        {isSearchMode ? (
          <SearchResultsServer 
            searchQuery={searchQuery}
            sort={sort}
            order={order}
            page={page}
          />
        ) : (
          <FeaturedRepositoriesServer 
            viewMode={viewMode}
            sort={sort}
            order={order}
          />
        )}
      </HomeClient>
    </div>
  );
}