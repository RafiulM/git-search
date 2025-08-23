import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  FileText,
  Star,
  GitFork,
  Calendar,
  ExternalLink,
  Database,
  Zap,
} from "lucide-react";
import Link from "next/link";
import type { RepositoryWithAnalysis } from '@/lib/types/api';

interface RepositoryListServerProps {
  repositories: RepositoryWithAnalysis[];
  viewMode: "list" | "grid";
  isSearchMode: boolean;
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

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export function RepositoryListServer({ repositories, viewMode, isSearchMode }: RepositoryListServerProps) {
  if (repositories.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <p className="text-muted-foreground">
            {isSearchMode 
              ? "No repositories found. Try adjusting your search terms." 
              : "No repositories available. Start by searching and analyzing some repositories!"
            }
          </p>
        </CardContent>
      </Card>
    );
  }

  if (isSearchMode) {
    // GitHub search results rendering
    const searchRepos = repositories as RepositoryWithAnalysis[];
    
    return (
      <div className="space-y-3">
        {searchRepos.map((repo) => (
          <Card key={repo.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <Link 
                        href={`/repository/${repo.author}/${repo.name}`}
                        className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        {repo.name}
                      </Link>
                      <a
                        href={repo.repo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                    
                    {/* <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        {formatNumber(repo.stargazers_count)}
                      </div>
                      <div className="flex items-center gap-1">
                        <GitFork className="w-3 h-3" />
                        {formatNumber(repo.forks_count)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(repo.updated_at)}
                      </div>
                    </div> */}
                  </div>
                  
                  <p className="text-muted-foreground text-sm mb-2 line-clamp-2">
                    {repo.analysis?.description || 'No description available'}
                  </p>

                  {/* <div className="flex flex-wrap gap-1">
                    {repo.language && (
                      <Badge variant="secondary" className="text-xs">{repo.language}</Badge>
                    )}
                    {repo.topics?.slice(0, 2).map((topic) => (
                      <Badge key={topic} variant="outline" className="text-xs">
                        {topic}
                      </Badge>
                    ))}
                    {repo.topics?.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{repo.topics.length - 2}
                      </Badge>
                    )}
                  </div> */}
                </div>

                <div className="flex flex-col gap-2 ml-4 shrink-0">
                  {repo.analysis ? (
                    <Link href={`/repository/${repo.author}/${repo.name}`}>
                      <Button variant="outline" size="sm">
                        <BarChart3 className="w-4 h-4 mr-1" />
                        View
                      </Button>
                    </Link>
                  ) : (
                    <form action="/api/analyze" method="post">
                      <input type="hidden" name="repo_url" value={repo.repo_url} />
                      <Button variant="outline" size="sm" type="submit">
                        <FileText className="w-4 h-4 mr-1" />
                        Analyze
                      </Button>
                    </form>
                  )}
                  
                  {repo.analysis?.created_at && (
                    <p className="text-xs text-muted-foreground text-center">
                      {formatDate(repo.analysis.created_at)}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Featured repositories rendering using exact styling from RepositoryCards
  const featuredRepos = repositories as RepositoryWithAnalysis[];
  
  // Extract owner/repo from GitHub URL
  const getOwnerRepoFromUrl = (repoUrl: string) => {
    try {
      const url = new URL(repoUrl);
      const pathParts = url.pathname.split('/').filter(Boolean);
      if (pathParts.length >= 2) {
        return `${pathParts[0]}/${pathParts[1]}`;
      }
      return '';
    } catch {
      return '';
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  if (viewMode === "grid") {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featuredRepos.map((repo) => (
          <Card key={repo.id} className="hover:shadow-lg transition-all duration-200 hover:scale-[1.02]">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-3">
                <Link 
                  href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}
                  className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 line-clamp-1"
                >
                  {repo.name}
                </Link>
                <a
                  href={repo.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              
              <p className="text-muted-foreground text-sm mb-3 line-clamp-2 min-h-[2.5rem]">
                {repo.analysis?.description || 'No description available'}
              </p>

              <div className="flex flex-wrap gap-1 mb-4">
                {repo.author && (
                  <Badge variant="secondary" className="text-xs">
                    {repo.author}
                  </Badge>
                )}
                {repo.branch && (
                  <Badge variant="outline" className="text-xs">
                    {repo.branch}
                  </Badge>
                )}
              </div>

              {/* Statistics Grid */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <FileText className="w-3 h-3 text-blue-600" />
                  <div>
                    <div className="text-xs font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.total_lines || 0)}
                    </div>
                    <div className="text-[10px] text-muted-foreground">Lines</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <Database className="w-3 h-3 text-green-600" />
                  <div>
                    <div className="text-xs font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.total_files_found || 0)}
                    </div>
                    <div className="text-[10px] text-muted-foreground">Files</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <BarChart3 className="w-3 h-3 text-purple-600" />
                  <div>
                    <div className="text-xs font-semibold text-slate-600">
                      {formatBytes(repo.analysis?.estimated_size_bytes || 0)}
                    </div>
                    <div className="text-[10px] text-muted-foreground">Size</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <Zap className="w-3 h-3 text-orange-600" />
                  <div>
                    <div className="text-xs font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.estimated_tokens || 0)}
                    </div>
                    <div className="text-[10px] text-muted-foreground">Tokens</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Calendar className="w-3 h-3" />
                  {formatDate(repo.updated_at)}
                </div>
                <Link href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}>
                  <Button variant="outline" size="sm" className="text-xs">
                    <BarChart3 className="w-3 h-3 mr-1" />
                    Analyze
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // List view for featured repositories
  return (
    <div className="space-y-4">
      {featuredRepos.map((repo) => (
        <Card key={repo.id} className="hover:shadow-lg transition-shadow">
          <CardContent>
            <div className="flex-1">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <Link 
                    href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}
                    className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    {repo.name}
                  </Link>
                  <a
                    href={repo.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(repo.updated_at)}
                    </div>
                  </div>
                  <Link href={`/repository/${getOwnerRepoFromUrl(repo.repo_url)}`}>
                    <Button variant="outline" size="sm">
                      <BarChart3 className="w-4 h-4 mr-1" />
                      View Analysis
                    </Button>
                  </Link>
                </div>
              </div>
            
              <p className="text-muted-foreground text-sm mb-2 line-clamp-2">
                {repo.analysis?.description || 'No description available'}
              </p>

              <div className="flex flex-wrap gap-1 mb-3">
                {repo.author && (
                  <Badge variant="secondary" className="text-xs">
                    {repo.author}
                  </Badge>
                )}
                {repo.branch && (
                  <Badge variant="outline" className="text-xs">
                    {repo.branch}
                  </Badge>
                )}
              </div>

              {/* Statistics with Icons */}
              <div className="grid grid-cols-4 gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-600" />
                  <div>
                    <div className="text-sm font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.total_lines || 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">Lines</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-green-600" />
                  <div>
                    <div className="text-sm font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.total_files_found || 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">Files</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-purple-600" />
                  <div>
                    <div className="text-sm font-semibold text-slate-600">
                      {formatBytes(repo.analysis?.estimated_size_bytes || 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">Size</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-orange-600" />
                  <div>
                    <div className="text-sm font-semibold text-slate-600">
                      {formatNumber(repo.analysis?.estimated_tokens || 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">Tokens</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}