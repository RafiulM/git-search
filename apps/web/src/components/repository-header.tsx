import { 
  Calendar, 
  ExternalLink,
  Code,
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Link from 'next/link';
import { Repository } from '@/lib/types/api';

interface RepositoryHeaderProps {
  repository: Repository;
  owner: string;
  repo: string;
  firstDocumentType: string;
  children: React.ReactNode;
}

export function RepositoryHeader({ 
  repository, 
  owner, 
  repo, 
  firstDocumentType, 
  children 
}: RepositoryHeaderProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <>
      {/* Repository Header */}
      <div className="mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">{repository.name}</h1>
            <p className="text-muted-foreground text-lg">
              {repository.author ? `by ${repository.author}` : 'Repository'}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <a href={repository.repo_url} target="_blank" rel="noopener noreferrer">
              <button className="bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800">
                <ExternalLink className="w-4 h-4 mr-1 inline" />
                View on GitHub
              </button>
            </a>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex flex-wrap items-center gap-6 text-sm">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span className="text-muted-foreground">Created {formatDate(repository.created_at)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span className="text-muted-foreground">Updated {formatDate(repository.updated_at)}</span>
          </div>
          {repository.branch && (
            <div className="flex items-center gap-1">
              <Code className="w-4 h-4" />
              <span className="text-muted-foreground">Branch: {repository.branch}</span>
            </div>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
          <TabsTrigger value="files">Files</TabsTrigger>
          <TabsTrigger value="documentation" asChild>
            <Link href={`/repository/${owner}/${repo}/docs/${firstDocumentType}`}>
              Documentation
            </Link>
          </TabsTrigger>
        </TabsList>

        {children}
      </Tabs>
    </>
  );
}