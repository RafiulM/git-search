"use client";

// Authentication removed
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  GitBranch,
  BarChart3,
  FileText,
  Zap,
  Database,
  Star,
  GitFork,
  Calendar,
  ExternalLink,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";

// Dummy repository data with AI-focused statistics
const dummyRepositories = [
  {
    id: 1,
    name: "facebook/react",
    description: "The library for web and native user interfaces",
    language: "JavaScript",
    stars: 227000,
    forks: 46000,
    watchers: 6800,
    lastUpdated: "2024-01-15",
    stats: {
      linesOfCode: 125000,
      characters: 4200000,
      files: 1250,
      storageSize: "15.2 MB",
      tokenEstimates: {
        gpt4: 1200000,
        claude: 933000,
        gemini: 1050000
      },
      complexity: 7.2,
      maintainability: 82.5
    },
    topics: ["javascript", "react", "frontend", "library", "components"]
  },
  {
    id: 2,
    name: "microsoft/vscode",
    description: "Visual Studio Code - Open Source Build",
    language: "TypeScript",
    stars: 163000,
    forks: 28000,
    watchers: 3500,
    lastUpdated: "2024-01-14",
    stats: {
      linesOfCode: 890000,
      characters: 28500000,
      files: 8500,
      storageSize: "145.8 MB",
      tokenEstimates: {
        gpt4: 8140000,
        claude: 6333000,
        gemini: 7125000
      },
      complexity: 8.9,
      maintainability: 75.3
    },
    topics: ["typescript", "editor", "electron", "ide", "code-editor"]
  },
  {
    id: 3,
    name: "vercel/next.js",
    description: "The React Framework for the Web",
    language: "JavaScript",
    stars: 125000,
    forks: 26000,
    watchers: 1800,
    lastUpdated: "2024-01-16",
    stats: {
      linesOfCode: 320000,
      characters: 12800000,
      files: 3200,
      storageSize: "52.4 MB",
      tokenEstimates: {
        gpt4: 3657000,
        claude: 2844000,
        gemini: 3200000
      },
      complexity: 6.8,
      maintainability: 85.7
    },
    topics: ["nextjs", "react", "framework", "fullstack", "ssr"]
  },
  {
    id: 4,
    name: "pytorch/pytorch",
    description: "Tensors and Dynamic neural networks in Python",
    language: "Python",
    stars: 82000,
    forks: 22000,
    watchers: 2100,
    lastUpdated: "2024-01-13",
    stats: {
      linesOfCode: 1500000,
      characters: 52000000,
      files: 12000,
      storageSize: "380.5 MB",
      tokenEstimates: {
        gpt4: 14857000,
        claude: 11555000,
        gemini: 13000000
      },
      complexity: 9.1,
      maintainability: 68.2
    },
    topics: ["python", "pytorch", "machine-learning", "deep-learning", "ai"]
  }
];

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="text-center py-12 sm:py-16 relative px-4">
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
          <div className="flex items-center gap-2 sm:gap-3">
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

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search repositories (e.g., react typescript, machine learning python)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-base"
              />
            </div>
            <Button type="submit" size="lg" className="h-12 px-8 bg-purple-600 hover:bg-purple-700 text-white">
              Search
            </Button>
          </div>
        </form>

      </div>

      <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-5xl">
        {/* Featured Repositories - Moved to Top */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-2">Featured Repositories</h2>
            <p className="text-muted-foreground">
              Popular repositories with comprehensive AI-focused analysis
            </p>
          </div>
          
          <div className="space-y-4">
            {dummyRepositories.map((repo) => (
              <Card key={repo.id} className="hover:shadow-lg transition-shadow">
                <CardContent>
                                      <div className="flex-1">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <Link 
                            href={`/repository/${repo.name.replace('/', '-')}`}
                            className="text-lg font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {repo.name}
                          </Link>
                          <a
                            href={`https://github.com/${repo.name}`}
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
                              <Star className="w-3 h-3" />
                              {formatNumber(repo.stars)}
                            </div>
                            <div className="flex items-center gap-1">
                              <GitFork className="w-3 h-3" />
                              {formatNumber(repo.forks)}
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {formatDate(repo.lastUpdated)}
                            </div>
                          </div>
                          <Link href={`/repository/${repo.name.replace('/', '-')}`}>
                            <Button variant="outline" size="sm">
                              <BarChart3 className="w-4 h-4 mr-1" />
                              Analyze
                            </Button>
                          </Link>
                        </div>
                      </div>
                    
                    <p className="text-muted-foreground text-sm mb-2 line-clamp-2">
                      {repo.description}
                    </p>

                    <div className="flex flex-wrap gap-1 mb-3">
                      <Badge variant="secondary" className="text-xs">
                        {repo.language}
                      </Badge>
                      {repo.topics.slice(0, 2).map((topic) => (
                        <Badge key={topic} variant="outline" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                      {repo.topics.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{repo.topics.length - 2}
                        </Badge>
                      )}
                    </div>

                                          {/* Statistics with Icons */}
                      <div className="grid grid-cols-4 gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatNumber(repo.stats.linesOfCode)}
                            </div>
                            <div className="text-xs text-muted-foreground">Lines</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Database className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {repo.stats.files}
                            </div>
                            <div className="text-xs text-muted-foreground">Files</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {repo.stats.storageSize}
                            </div>
                            <div className="text-xs text-muted-foreground">Size</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Zap className="w-4 h-4 text-blue-600" />
                          <div>
                            <div className="text-sm font-semibold text-slate-600">
                              {formatNumber(repo.stats.tokenEstimates.gpt4)}
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

          <div className="text-center mt-8">
            <Link href="/search">
              <Button size="lg">
                <Search className="w-4 h-4 mr-2" />
                Explore More Repositories
              </Button>
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
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

      </main>
    </div>
  );
}
