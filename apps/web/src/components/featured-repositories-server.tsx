import { Suspense } from 'react';
import { listRepositories } from '@/lib/api';
import { RepositoryListServer } from './repository-list-server';
import { RepositorySkeleton } from './repository-skeleton';
import { RepositoryWithAnalysis } from '@/lib/types/api';

interface FeaturedRepositoriesProps {
  viewMode: "list" | "grid";
  sort: string;
  order: string;
}

async function FeaturedRepositoriesContent({ viewMode, sort, order }: FeaturedRepositoriesProps) {
  try {
    const response = await listRepositories({
      limit: 12, // Good number for grid display
      include_analysis: true,
      include_ai_summary: false
    });

    // Sort repositories based on selected criteria
    const sortRepositories = (repos: (RepositoryWithAnalysis)[]) => {
      return [...repos].sort((a, b) => {
        let aValue: number | string = 0;
        let bValue: number | string = 0;

        switch (sort) {
          case 'stars':
            // Use estimated tokens as a proxy for "stars" since our repos don't have GitHub stars
            aValue = (a as RepositoryWithAnalysis).analysis?.estimated_tokens || 0;
            bValue = (b as RepositoryWithAnalysis).analysis?.estimated_tokens || 0;
            break;
          case 'forks':
            // Use total files as a proxy for "forks"
            aValue = (a as RepositoryWithAnalysis).analysis?.total_files_found || 0;
            bValue = (b as RepositoryWithAnalysis).analysis?.total_files_found || 0;
            break;
          case 'updated':
            aValue = new Date(a.updated_at || '').getTime();
            bValue = new Date(b.updated_at || '').getTime();
            break;
          case 'created':
            aValue = new Date(a.created_at || '').getTime();
            bValue = new Date(b.created_at || '').getTime();
            break;
          default:
            aValue = (a as RepositoryWithAnalysis).analysis?.estimated_tokens || 0;
            bValue = (b as RepositoryWithAnalysis).analysis?.estimated_tokens || 0;
        }

        const comparison = aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
        return order === 'desc' ? -comparison : comparison;
      });
    };

    const sortedRepositories = sortRepositories(response.repositories);

    return (
      <RepositoryListServer 
        repositories={sortedRepositories}
        viewMode={viewMode}
        isSearchMode={false}
      />
    );
  } catch (error) {
    console.error('Failed to fetch featured repositories:', error);
    return (
      <RepositoryListServer 
        repositories={[]}
        viewMode={viewMode}
        isSearchMode={false}
      />
    );
  }
}

export function FeaturedRepositoriesServer({ viewMode, sort, order }: FeaturedRepositoriesProps) {
  return (
    <Suspense fallback={<RepositorySkeleton viewMode={viewMode} count={12} />}>
      <FeaturedRepositoriesContent viewMode={viewMode} sort={sort} order={order} />
    </Suspense>
  );
}