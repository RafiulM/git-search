"use client";

import { useState, useEffect } from "react";
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
  ExternalLink,
  TrendingUp,
  Users,
  Clock,
  Code2,
  Sparkles,
  ArrowRight,
  CheckCircle,
  BookOpen,
  Brain,
  Activity,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useFeaturedRepositories } from "@/hooks/use-featured-repositories";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentStat, setCurrentStat] = useState(0);
  const router = useRouter();
  const { data: featuredRepositories, isLoading, error } = useFeaturedRepositories(4);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Stats animation
  const stats = [
    { label: "Repositories Analyzed", value: "10K+", icon: Database },
    { label: "Lines of Code Processed", value: "500M+", icon: Code2 },
    { label: "AI Insights Generated", value: "25K+", icon: Brain },
    { label: "Developers Served", value: "2K+", icon: Users },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStat((prev) => (prev + 1) % stats.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [stats.length]);

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

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <GitBranch className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Git Search
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/search" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Search
            </Link>
            <Link href="/dashboard" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="text-center py-16 sm:py-24 relative px-4">
        <div className="container mx-auto max-w-6xl">
          {/* Main Hero Content */}
          <div className="mb-12">
            <div className="flex flex-col items-center justify-center gap-6 mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-3xl opacity-20 scale-150"></div>
                <GitBranch className="relative w-16 h-16 sm:w-20 sm:h-20 text-blue-600 animate-pulse" />
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-400 bg-clip-text text-transparent leading-tight">
                Git Search
              </h1>
            </div>
            <p className="text-xl sm:text-2xl text-muted-foreground max-w-4xl mx-auto px-4 mb-6 leading-relaxed">
              The ultimate GitHub repository directory with AI-powered insights, comprehensive analysis, and smart recommendations
            </p>
            
            {/* Value Proposition */}
            <div className="flex flex-wrap items-center justify-center gap-4 mb-12 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>AI-Powered Analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Real-time Metrics</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Code Intelligence</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Developer Insights</span>
              </div>
            </div>
          </div>

          {/* Enhanced Search Bar */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-16">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              <div className="relative flex gap-2 p-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    type="text"
                    placeholder="Search repositories (e.g., react typescript, machine learning python, nextjs)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-12 pr-4 h-14 text-base border-0 bg-transparent focus:ring-0 focus:outline-none"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="h-14 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <Search className="w-5 h-5 mr-2" />
                  Search
                </Button>
              </div>
            </div>
            
            {/* Search Suggestions */}
            <div className="flex flex-wrap justify-center gap-2 mt-6">
              <span className="text-sm text-muted-foreground mr-2">Popular searches:</span>
              {["React", "TypeScript", "Next.js", "Python ML", "Vue.js", "Node.js"].map((term) => (
                <button
                  key={term}
                  onClick={() => {
                    setSearchQuery(term);
                    router.push(`/search?q=${encodeURIComponent(term)}`);
                  }}
                  className="text-xs px-3 py-1 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-gray-600 dark:text-gray-300 transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </form>

          {/* Animated Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto mb-16">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card 
                  key={index} 
                  className={`text-center p-6 transition-all duration-500 ${
                    currentStat === index 
                      ? 'scale-105 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800' 
                      : 'hover:scale-105'
                  }`}
                >
                  <Icon className={`w-8 h-8 mx-auto mb-3 ${currentStat === index ? 'text-blue-600' : 'text-gray-600'}`} />
                  <div className="text-2xl font-bold text-foreground mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

      <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-6xl">
        {/* How It Works Section */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How Git Search Works</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Discover, analyze, and understand GitHub repositories like never before
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="text-center p-8 relative overflow-hidden group hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="w-16 h-16 mx-auto mb-6 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                  <Search className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">1. Search & Discover</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Enter keywords, topics, or specific technologies to find relevant repositories from GitHub&apos;s vast ecosystem.
                </p>
              </div>
            </Card>
            
            <Card className="text-center p-8 relative overflow-hidden group hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="w-16 h-16 mx-auto mb-6 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                  <Brain className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">2. AI Analysis</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Our AI engines analyze code structure, complexity, dependencies, and generate intelligent insights about each repository.
                </p>
              </div>
            </Card>
            
            <Card className="text-center p-8 relative overflow-hidden group hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="w-16 h-16 mx-auto mb-6 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                  <Activity className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-4">3. Get Insights</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Access detailed metrics, documentation, token estimates, and make informed decisions about code adoption.
                </p>
              </div>
            </Card>
          </div>
        </section>

        {/* Featured Repositories */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Sparkles className="w-6 h-6 text-yellow-500" />
              <h2 className="text-3xl font-bold">Featured Repositories</h2>
              <Sparkles className="w-6 h-6 text-yellow-500" />
            </div>
            <p className="text-xl text-muted-foreground">
              Popular repositories with comprehensive AI-focused analysis
            </p>
          </div>
          
          <div className="grid gap-6">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 3 }).map((_, index) => (
                <Card key={index} className="hover:shadow-xl transition-all duration-300 overflow-hidden">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <Skeleton className="h-6 w-2/3" />
                          <Skeleton className="h-4 w-full" />
                        </div>
                        <Skeleton className="h-10 w-32" />
                      </div>
                      <div className="flex gap-2">
                        <Skeleton className="h-6 w-20" />
                        <Skeleton className="h-6 w-20" />
                        <Skeleton className="h-6 w-20" />
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                        {Array.from({ length: 4 }).map((_, i) => (
                          <div key={i} className="text-center">
                            <Skeleton className="h-8 w-8 mx-auto mb-2 rounded-full" />
                            <Skeleton className="h-4 w-12 mx-auto mb-1" />
                            <Skeleton className="h-3 w-16 mx-auto" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : error ? (
              // Error state
              <Card className="border-red-200 dark:border-red-800">
                <CardContent className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                    <ExternalLink className="w-8 h-8 text-red-600" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Unable to Load Repositories</h3>
                  <p className="text-muted-foreground mb-4">
                    We&apos;re having trouble fetching featured repositories. Please try again later.
                  </p>
                  <Button variant="outline" onClick={() => window.location.reload()}>
                    Try Again
                  </Button>
                </CardContent>
              </Card>
            ) : featuredRepositories && featuredRepositories.length > 0 ? (
              // Real data
              featuredRepositories.slice(0, 3).map((repo) => (
                <Card key={repo.id} className="group hover:shadow-xl transition-all duration-300 overflow-hidden border-0 bg-gradient-to-r from-white to-gray-50 dark:from-gray-800 dark:to-gray-900">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Link 
                            href={`/repository/${repo.name.replace('/', '-')}`}
                            className="text-xl font-bold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
                          >
                            {repo.name}
                          </Link>
                          <a
                            href={repo.repo_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                          >
                            <ExternalLink className="w-5 h-5" />
                          </a>
                          <div className="flex items-center gap-1 text-sm text-green-600">
                            <TrendingUp className="w-4 h-4" />
                            <span>Trending</span>
                          </div>
                        </div>
                        
                        <p className="text-muted-foreground mb-4 leading-relaxed">
                          {repo.description || 'No description available'}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-4">
                          {repo.author && (
                            <Badge variant="secondary" className="text-sm px-3 py-1">
                              <Users className="w-3 h-3 mr-1" />
                              {repo.author}
                            </Badge>
                          )}
                          {repo.branch && (
                            <Badge variant="outline" className="text-sm px-3 py-1">
                              <GitBranch className="w-3 h-3 mr-1" />
                              {repo.branch}
                            </Badge>
                          )}
                          <Badge variant="outline" className="text-sm px-3 py-1">
                            <Clock className="w-3 h-3 mr-1" />
                            {formatDate(repo.updated_at)}
                          </Badge>
                        </div>
                      </div>

                      <Link href={`/repository/${repo.name.replace('/', '-')}`}>
                        <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
                          <BarChart3 className="w-4 h-4 mr-2" />
                          View Analysis
                          <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                      </Link>
                    </div>

                    {/* Enhanced Statistics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
                      <div className="text-center group/stat hover:scale-105 transition-transform">
                        <div className="w-12 h-12 mx-auto mb-2 bg-blue-100 dark:bg-blue-900/40 rounded-full flex items-center justify-center group-hover/stat:bg-blue-200 dark:group-hover/stat:bg-blue-800/40 transition-colors">
                          <FileText className="w-6 h-6 text-blue-600" />
                        </div>
                        <div className="text-lg font-bold text-foreground">
                          {formatNumber(repo.stats?.total_lines || 0)}
                        </div>
                        <div className="text-xs text-muted-foreground font-medium">Lines of Code</div>
                      </div>
                      <div className="text-center group/stat hover:scale-105 transition-transform">
                        <div className="w-12 h-12 mx-auto mb-2 bg-purple-100 dark:bg-purple-900/40 rounded-full flex items-center justify-center group-hover/stat:bg-purple-200 dark:group-hover/stat:bg-purple-800/40 transition-colors">
                          <Database className="w-6 h-6 text-purple-600" />
                        </div>
                        <div className="text-lg font-bold text-foreground">
                          {formatNumber(repo.stats?.total_files_found || 0)}
                        </div>
                        <div className="text-xs text-muted-foreground font-medium">Files</div>
                      </div>
                      <div className="text-center group/stat hover:scale-105 transition-transform">
                        <div className="w-12 h-12 mx-auto mb-2 bg-green-100 dark:bg-green-900/40 rounded-full flex items-center justify-center group-hover/stat:bg-green-200 dark:group-hover/stat:bg-green-800/40 transition-colors">
                          <BarChart3 className="w-6 h-6 text-green-600" />
                        </div>
                        <div className="text-lg font-bold text-foreground">
                          {formatBytes(repo.stats?.estimated_size_bytes || 0)}
                        </div>
                        <div className="text-xs text-muted-foreground font-medium">Repository Size</div>
                      </div>
                      <div className="text-center group/stat hover:scale-105 transition-transform">
                        <div className="w-12 h-12 mx-auto mb-2 bg-yellow-100 dark:bg-yellow-900/40 rounded-full flex items-center justify-center group-hover/stat:bg-yellow-200 dark:group-hover/stat:bg-yellow-800/40 transition-colors">
                          <Zap className="w-6 h-6 text-yellow-600" />
                        </div>
                        <div className="text-lg font-bold text-foreground">
                          {formatNumber(repo.stats?.estimated_tokens || 0)}
                        </div>
                        <div className="text-xs text-muted-foreground font-medium">AI Tokens</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              // No data state
              <Card className="border-dashed border-2 border-gray-300 dark:border-gray-700">
                <CardContent className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                    <Search className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">No Featured Repositories</h3>
                  <p className="text-muted-foreground mb-4">
                    Start by analyzing some repositories to see them featured here!
                  </p>
                  <Link href="/search">
                    <Button>
                      <Search className="w-4 h-4 mr-2" />
                      Start Exploring
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="text-center mt-12">
            <Link href="/search">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200">
                <Search className="w-5 h-5 mr-2" />
                Explore All Repositories
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
        </section>

        {/* Enhanced Features Section */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Advanced insights and analysis tools that transform how you understand GitHub repositories
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="group text-center p-6 hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 border-blue-200 dark:border-blue-800 hover:scale-105">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center group-hover:bg-blue-200 dark:group-hover:bg-blue-800/40 transition-colors">
                <BarChart3 className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Code Statistics</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Comprehensive metrics including lines of code, file counts, complexity analysis, and code quality indicators
              </p>
            </Card>
            
            <Card className="group text-center p-6 hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800 hover:scale-105">
              <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center group-hover:bg-green-200 dark:group-hover:bg-green-800/40 transition-colors">
                <Zap className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold mb-3">AI Token Estimates</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Accurate token estimates for GPT-4, Claude, Gemini, and other AI models to optimize your AI workflow costs
              </p>
            </Card>
            
            <Card className="group text-center p-6 hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 border-purple-200 dark:border-purple-800 hover:scale-105">
              <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center group-hover:bg-purple-200 dark:group-hover:bg-purple-800/40 transition-colors">
                <BookOpen className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Smart Documentation</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                AI-generated documentation, architecture diagrams, and comprehensive code explanations
              </p>
            </Card>
            
            <Card className="group text-center p-6 hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/10 dark:to-red-900/10 border-orange-200 dark:border-orange-800 hover:scale-105">
              <div className="w-16 h-16 mx-auto mb-4 bg-orange-100 dark:bg-orange-900/30 rounded-xl flex items-center justify-center group-hover:bg-orange-200 dark:group-hover:bg-orange-800/40 transition-colors">
                <Code2 className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Tech Stack Analysis</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Detailed language breakdown, framework detection, dependency analysis, and technology recommendations
              </p>
            </Card>
          </div>
        </section>

        {/* Call to Action Section */}
        <section className="mb-20">
          <Card className="relative overflow-hidden bg-gradient-to-br from-blue-600 to-purple-700 border-0">
            <div className="absolute inset-0 bg-black/20"></div>
            <CardContent className="relative p-12 text-center text-white">
              <div className="max-w-3xl mx-auto">
                <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
                <p className="text-xl mb-8 text-blue-100">
                  Join thousands of developers who use Git Search to discover, analyze, and understand code repositories with AI-powered insights.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/search">
                    <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200">
                      <Search className="w-5 h-5 mr-2" />
                      Start Searching
                    </Button>
                  </Link>
                  <Link href="/dashboard">
                    <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 text-lg font-semibold rounded-xl transition-all duration-200">
                      <BarChart3 className="w-5 h-5 mr-2" />
                      View Dashboard
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Social Proof / Stats Section */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Trusted by Developers Worldwide</h2>
            <p className="text-xl text-muted-foreground">
              Join our growing community of developers who rely on Git Search for code insights
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="text-center p-8 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800">
              <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-green-600 mb-2">99.9%</h3>
              <p className="text-muted-foreground">Analysis Accuracy</p>
            </Card>
            
            <Card className="text-center p-8 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 border-blue-200 dark:border-blue-800">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-blue-600 mb-2">&lt; 2s</h3>
              <p className="text-muted-foreground">Average Response Time</p>
            </Card>
            
            <Card className="text-center p-8 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 border-purple-200 dark:border-purple-800">
              <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-purple-600 mb-2">24/7</h3>
              <p className="text-muted-foreground">Always Available</p>
            </Card>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <GitBranch className="w-8 h-8 text-blue-600" />
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Git Search
                </span>
              </div>
              <p className="text-muted-foreground mb-4 max-w-md">
                The ultimate GitHub repository directory with AI-powered insights, comprehensive analysis, and smart recommendations for developers worldwide.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span>Free to use</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span>Always up-to-date</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <div className="space-y-2">
                <Link href="/search" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Search Repositories
                </Link>
                <Link href="/dashboard" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Dashboard
                </Link>
                <Link href="/favorites" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Favorites
                </Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Features</h3>
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">AI Analysis</div>
                <div className="text-sm text-muted-foreground">Code Statistics</div>
                <div className="text-sm text-muted-foreground">Token Estimates</div>
                <div className="text-sm text-muted-foreground">Smart Documentation</div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-200 dark:border-gray-800 mt-8 pt-8 text-center">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Git Search. Built with ❤️ for developers.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
