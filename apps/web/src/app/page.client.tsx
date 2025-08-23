'use client';

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  BarChart3,
  FileText,
  Zap,
  Database,
  Filter,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { ViewToggle } from "@/components/view-toggle";
import { ReactNode } from 'react';

interface HomeClientProps {
  children: ReactNode;
  searchQuery: string;
  sort: string;
  order: string;
  page: number;
  viewMode: "list" | "grid";
  isSearchMode: boolean;
}

export default function HomeClient({ 
  children,
  searchQuery, 
  sort: initialSort, 
  order: initialOrder, 
  page: initialPage,
  viewMode: initialViewMode,
  isSearchMode 
}: HomeClientProps) {
  const [viewMode, setViewMode] = useState<"list" | "grid">(initialViewMode);
  const [sort, setSort] = useState(initialSort);
  const [order, setOrder] = useState(initialOrder);
  const [page] = useState(initialPage);
  const router = useRouter();

  // Update sort/order/view via URL params
  const updateUrlParams = (newSort?: string, newOrder?: string, newViewMode?: string) => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if ((newSort || sort) !== 'stars') params.set('sort', newSort || sort);
    if ((newOrder || order) !== 'desc') params.set('order', newOrder || order);
    if ((newViewMode || viewMode) !== 'grid') params.set('view', newViewMode || viewMode);
    if (page !== 1) params.set('page', page.toString());
    
    const queryString = params.toString();
    const newUrl = queryString ? `/?${queryString}` : '/';
    router.push(newUrl);
  };

  const handleSortChange = (newSort: string) => {
    setSort(newSort);
    updateUrlParams(newSort, order);
  };

  const handleOrderChange = (newOrder: string) => {
    setOrder(newOrder);
    updateUrlParams(sort, newOrder);
  };

  const handleViewModeChange = (newViewMode: "list" | "grid") => {
    setViewMode(newViewMode);
    updateUrlParams(sort, order, newViewMode);
  };

  return (
    <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-6xl">
        {/* Filters and Sort Controls - Right above repositories */}
        <div className="flex flex-col sm:flex-row gap-4 sm:gap-0 items-center justify-between mb-6 w-full">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              <span className="text-sm">Sort by:</span>
            </div>
            <Select value={sort} onValueChange={handleSortChange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="stars">Stars</SelectItem>
                <SelectItem value="forks">Forks</SelectItem>
                <SelectItem value="updated">Updated</SelectItem>
                <SelectItem value="created">Created</SelectItem>
              </SelectContent>
            </Select>
            <Select value={order} onValueChange={handleOrderChange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Descending</SelectItem>
                <SelectItem value="asc">Ascending</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <ViewToggle viewMode={viewMode} onViewModeChange={handleViewModeChange} />
          </div>
        </div>
        
        {/* Repository Content - Server Rendered */}
        <div className="mb-16">
          {children}
        </div>

        {/* Feature Cards - Only show when not in search mode */}
        {!isSearchMode && (
          <div className="mb-12">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Platform Features</h2>
              <p className="text-muted-foreground">Advanced insights and analysis tools for GitHub repositories</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
              <Card className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 border-blue-200 dark:border-blue-800">
                <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h3 className="font-semibold mb-1">Code Statistics</h3>
                <p className="text-sm text-muted-foreground">Lines of code, file counts, and complexity metrics</p>
              </Card>
              
              <Card className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800">
                <Zap className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold mb-1">AI Token Estimates</h3>
                <p className="text-sm text-muted-foreground">Estimates for GPT-4, Claude, and Gemini models</p>
              </Card>
              
              <Card className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 border-purple-200 dark:border-purple-800">
                <FileText className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <h3 className="font-semibold mb-1">Documentation</h3>
                <p className="text-sm text-muted-foreground">Auto-generated docs and architecture diagrams</p>
              </Card>
              
              <Card className="text-center p-4 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/10 dark:to-red-900/10 border-orange-200 dark:border-orange-800">
                <Database className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                <h3 className="font-semibold mb-1">Tech Stack Analysis</h3>
                <p className="text-sm text-muted-foreground">Language breakdown and technology insights</p>
              </Card>
            </div>
          </div>
        )}

      </main>
    );
}