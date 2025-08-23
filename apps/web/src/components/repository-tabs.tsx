import { BarChart3, CodeIcon, FileIcon, FolderIcon, HardDrive, Hash, Settings, Database, AlertTriangle, Calendar, Activity, Zap } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TabsContent } from '@/components/ui/tabs';
import { RepositoryTree } from '@/components/repository-tree';
import { DocumentationTab } from '@/components/documentation-tab';
import type { Repository, RepositoryAnalysis } from '@/lib/types/api';

// Utility functions
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

interface RepositoryTabsProps {
  repository: Repository;
  analysis: RepositoryAnalysis | null;
  owner: string;
  repo: string;
  firstDocumentType?: string;
}

export function RepositoryTabs({ 
  repository, 
  analysis, 
  owner, 
  repo, 
  firstDocumentType = '' 
}: RepositoryTabsProps) {
  return (
    <>
      <TabsContent value="overview" className="space-y-6">
        {/* Key Repository Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Key Statistics
            </CardTitle>
            <CardDescription>
              Essential metrics for this repository
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analysis ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="flex items-center gap-3 p-4 border rounded-lg">
                  <CodeIcon className="w-8 h-8 text-blue-600" />
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {analysis.total_lines ? formatNumber(analysis.total_lines) : 'N/A'}
                    </div>
                    <div className="text-sm text-muted-foreground">Lines of Code</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 border rounded-lg">
                  <FileIcon className="w-8 h-8 text-green-600" />
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {analysis.total_files_found || 'N/A'}
                    </div>
                    <div className="text-sm text-muted-foreground">Files</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 border rounded-lg">
                  <HardDrive className="w-8 h-8 text-purple-600" />
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {analysis.estimated_size_bytes ? formatBytes(analysis.estimated_size_bytes) : 'N/A'}
                    </div>
                    <div className="text-sm text-muted-foreground">Storage</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 border rounded-lg">
                  <FolderIcon className="w-8 h-8 text-cyan-600" />
                  <div>
                    <div className="text-2xl font-bold text-cyan-600">
                      {analysis.total_directories || 'N/A'}
                    </div>
                    <div className="text-sm text-muted-foreground">Directories</div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">No analysis data available</p>
            )}
          </CardContent>
        </Card>

        {/* Repository Info */}
        <Card>
          <CardHeader>
            <CardTitle>Repository Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Repository URL</span>
              <span className="font-medium text-sm">{repository.repo_url}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Author</span>
              <span className="font-medium">{repository.author || 'Unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Branch</span>
              <span className="font-medium">{repository.branch || 'main'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span className="font-medium">{formatDate(repository.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Last Updated</span>
              <span className="font-medium">{formatDate(repository.updated_at)}</span>
            </div>
            {analysis && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Analyzed</span>
                <span className="font-medium">{formatDate(analysis.created_at)}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="statistics">
        {analysis ? (
          <div className="space-y-6">
            {/* Comprehensive Code Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Comprehensive Code Metrics
                </CardTitle>
                <CardDescription>
                  Detailed statistics and analysis data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <CodeIcon className="w-8 h-8 text-blue-600" />
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {analysis.total_lines ? formatNumber(analysis.total_lines) : 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Total Lines</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <Hash className="w-8 h-8 text-green-600" />
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {analysis.total_characters ? formatNumber(analysis.total_characters) : 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Characters</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <FileIcon className="w-8 h-8 text-purple-600" />
                    <div>
                      <div className="text-2xl font-bold text-purple-600">
                        {analysis.total_files_found || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Files Found</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <Settings className="w-8 h-8 text-orange-600" />
                    <div>
                      <div className="text-2xl font-bold text-orange-600">
                        {analysis.files_processed || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Files Processed</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <FolderIcon className="w-8 h-8 text-cyan-600" />
                    <div>
                      <div className="text-2xl font-bold text-cyan-600">
                        {analysis.total_directories || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Directories</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg">
                    <HardDrive className="w-8 h-8 text-indigo-600" />
                    <div>
                      <div className="text-2xl font-bold text-indigo-600">
                        {analysis.estimated_size_bytes ? formatBytes(analysis.estimated_size_bytes) : 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Storage Size</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Token Estimates */}
            {analysis.estimated_tokens && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    AI Token Estimates
                  </CardTitle>
                  <CardDescription>
                    Estimated tokens for AI processing and analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3 p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                    <Zap className="w-12 h-12 text-blue-600" />
                    <div>
                      <div className="text-3xl font-bold text-blue-600">
                        {formatNumber(analysis.estimated_tokens)}
                      </div>
                      <div className="text-lg text-muted-foreground">Estimated Tokens</div>
                      <div className="text-sm text-muted-foreground">For AI model processing</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Analysis Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  Analysis Details
                </CardTitle>
                <CardDescription>
                  Processing details and analysis metadata
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                        <span className="text-muted-foreground">Binary Files Skipped</span>
                      </div>
                      <span className="font-medium">{analysis.binary_files_skipped || '0'}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-orange-600" />
                        <span className="text-muted-foreground">Large Files Skipped</span>
                      </div>
                      <span className="font-medium">{analysis.large_files_skipped || '0'}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <span className="text-muted-foreground">Encoding Errors</span>
                      </div>
                      <span className="font-medium">{analysis.encoding_errors || '0'}</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Settings className="w-5 h-5 text-blue-600" />
                        <span className="text-muted-foreground">Analysis Version</span>
                      </div>
                      <span className="font-medium">{analysis.analysis_version}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-purple-600" />
                        <span className="text-muted-foreground">Analyzed On</span>
                      </div>
                      <span className="font-medium">{formatDate(analysis.created_at)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <Activity className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Statistics Available</h3>
              <p className="text-muted-foreground">
                This repository hasn&apos;t been analyzed yet.
              </p>
            </CardContent>
          </Card>
        )}
      </TabsContent>

      <TabsContent value="files">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FolderIcon className="w-5 h-5" />
              Repository File Structure
            </CardTitle>
            <CardDescription>
              Explore the repository files and folders with an interactive tree view
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analysis && analysis.tree_structure ? (
              <RepositoryTree treeString={analysis.tree_structure} />
            ) : (
              <div className="text-center py-12">
                <FolderIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">No File Structure Available</h3>
                <p className="text-muted-foreground">
                  File structure analysis is not available for this repository.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value={firstDocumentType}>
        <DocumentationTab 
          repositoryId={repository.id}
          owner={owner} 
          repo={repo} 
        />
      </TabsContent>
    </>
  );
}