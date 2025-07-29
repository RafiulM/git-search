"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { useState } from "react";
import Chat from "@/components/chat";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { checkEnvironmentVariables } from "@/lib/env-check";
import {
  CheckCircle,
  AlertCircle,
  Zap,
  Database,
  Shield,
  ExternalLink,
  Search,
  GitBranch,
  BarChart3,
  FileText,
  Heart,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Home() {
  const envStatus = checkEnvironmentVariables();
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="text-center py-12 sm:py-16 relative px-4">
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <SignedOut>
              <SignInButton>
                <Button size="sm" className="text-xs sm:text-sm">
                  Sign In
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/favorites">
                <Button variant="outline" size="sm">
                  <Heart className="w-4 h-4 mr-1" />
                  Favorites
                </Button>
              </Link>
              <UserButton />
            </SignedIn>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-4">
          <GitBranch className="w-12 h-12 sm:w-16 sm:h-16 text-blue-600" />
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-400 bg-clip-text text-transparent">
            Git Search
          </h1>
        </div>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto px-4 mb-8">
          Discover GitHub repositories with AI-powered analysis and insights
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
            <Button type="submit" size="lg" className="h-12 px-8">
              Search
            </Button>
          </div>
        </form>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto mb-8">
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

      <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-5xl">
        {/* Quick Start Section */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold mb-4">Start Exploring</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
            <Link href="/search?q=react typescript">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl mb-2">⚛️</div>
                  <h3 className="font-semibold mb-1">React Projects</h3>
                  <p className="text-sm text-muted-foreground">Explore React and TypeScript repositories</p>
                </CardContent>
              </Card>
            </Link>
            
            <Link href="/search?q=machine learning python">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl mb-2">🤖</div>
                  <h3 className="font-semibold mb-1">ML & AI</h3>
                  <p className="text-sm text-muted-foreground">Machine learning and AI projects</p>
                </CardContent>
              </Card>
            </Link>
            
            <Link href="/search?q=backend golang">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl mb-2">🔧</div>
                  <h3 className="font-semibold mb-1">Backend APIs</h3>
                  <p className="text-sm text-muted-foreground">Server-side and API projects</p>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>

        {/* Setup Status for Development */}
        {(!envStatus.allConfigured) && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-500" />
                Development Setup
              </CardTitle>
              <CardDescription>
                Complete setup to enable all features
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-3 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10">
                  <div className="flex justify-center mb-2">
                    {envStatus.clerk ? (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    ) : (
                      <Shield className="w-6 h-6 text-blue-500" />
                    )}
                  </div>
                  <div className="font-semibold mb-1 text-sm">Clerk Auth</div>
                  <div className="text-xs text-muted-foreground mb-2">
                    {envStatus.clerk ? "✓ Ready" : "Setup required"}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open("https://dashboard.clerk.com", "_blank")}
                    className="w-full text-xs"
                  >
                    <ExternalLink className="w-3 h-3 mr-1" />
                    Setup
                  </Button>
                </div>

                <div className="text-center p-3 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10">
                  <div className="flex justify-center mb-2">
                    {envStatus.supabase ? (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    ) : (
                      <Database className="w-6 h-6 text-green-500" />
                    )}
                  </div>
                  <div className="font-semibold mb-1 text-sm">Supabase DB</div>
                  <div className="text-xs text-muted-foreground mb-2">
                    {envStatus.supabase ? "✓ Ready" : "Setup required"}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open("https://supabase.com/dashboard", "_blank")}
                    className="w-full text-xs"
                  >
                    <ExternalLink className="w-3 h-3 mr-1" />
                    Setup
                  </Button>
                </div>

                <div className="text-center p-3 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10">
                  <div className="flex justify-center mb-2">
                    <Zap className="w-6 h-6 text-purple-500" />
                  </div>
                  <div className="font-semibold mb-1 text-sm">GitHub Token</div>
                  <div className="text-xs text-muted-foreground mb-2">Optional</div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open("https://github.com/settings/tokens", "_blank")}
                    className="w-full text-xs"
                  >
                    <ExternalLink className="w-3 h-3 mr-1" />
                    Setup
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Chat Section */}
        <SignedIn>
          {envStatus.allConfigured && (
            <Card>
              <CardHeader>
                <CardTitle>AI Assistant</CardTitle>
                <CardDescription>
                  Chat with Claude about repositories and development
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Chat />
              </CardContent>
            </Card>
          )}
        </SignedIn>
      </main>
    </div>
  );
}
