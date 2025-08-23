import { Suspense } from 'react';
import { listRepositories } from '@/lib/api';
import { RepositoryListServer } from './repository-list-server';
import { SearchResultsSkeleton } from './repository-skeleton';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface SearchResultsProps {
  searchQuery: string;
  sort: string;
  order: string;
  page: number;
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
};

async function SearchResultsContent({ searchQuery, sort, order, page }: SearchResultsProps) {
  try {
    const searchResults = await listRepositories({
      search: searchQuery,
      skip: (page - 1) * 30,
      limit: 30,
      include_analysis: true,
      include_ai_summary: true
    });

    const buildPageUrl = (newPage: number) => {
      const params = new URLSearchParams();
      if (searchQuery) params.set('q', searchQuery);
      if (sort !== 'stars') params.set('sort', sort);
      if (order !== 'desc') params.set('order', order);
      if (newPage !== 1) params.set('page', newPage.toString());
      
      const queryString = params.toString();
      return queryString ? `/?${queryString}` : '/';
    };

    return (
      <>
        <div className="mb-6">
          <p className="text-sm text-muted-foreground">
            Found {formatNumber(searchResults.pagination.total)} analyzed repositories
          </p>
        </div>

        <RepositoryListServer 
          repositories={searchResults.repositories}
          viewMode="list" // Search results are always in list view for better scanning
          isSearchMode={true}
        />

        {/* Pagination */}
        {searchResults.pagination.has_more && (
          <div className="mt-8 flex justify-center gap-2">
            {page > 1 && (
              <Link href={buildPageUrl(page - 1)}>
                <Button variant="outline">
                  Previous
                </Button>
              </Link>
            )}
            <span className="flex items-center px-4 text-sm">
              Page {page} of {searchResults.pagination.total_pages}
            </span>
            {searchResults.pagination.has_more && (
              <Link href={buildPageUrl(page + 1)}>
                <Button variant="outline">
                  Next
                </Button>
              </Link>
            )}
          </div>
        )}
      </>
    );
  } catch (error) {
    console.error('Search error:', error);
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold mb-2">Search Error</h3>
          <p className="text-muted-foreground">
            Unable to load search results. Please try again.
          </p>
        </CardContent>
      </Card>
    );
  }
}

export function SearchResultsServer({ searchQuery, sort, order, page }: SearchResultsProps) {
  return (
    <Suspense fallback={<SearchResultsSkeleton />}>
      <SearchResultsContent 
        searchQuery={searchQuery}
        sort={sort}
        order={order}
        page={page}
      />
    </Suspense>
  );
}