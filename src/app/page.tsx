"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Zap,
  Database,
  Shield,
  Palette,
  Code2,
  Github,
  CheckCircle,
  Circle,
  Rocket,
  Sparkles,
  FileText,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import SetupGuide from "@/components/setup-guide";
import { checkEnvironmentVariables } from "@/lib/env-check";
import Chat from "@/components/chat";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

export default function Home() {
  const [envStatus, setEnvStatus] = useState({
    clerk: false,
    supabase: false,
    ai: false,
    allConfigured: false,
  });
  const [showSetup, setShowSetup] = useState(false);

  useEffect(() => {
    const status = checkEnvironmentVariables();
    setEnvStatus(status);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation Bar */}
      <nav className="p-4 sm:p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">CodeGuide Starter Kit</h1>
              <p className="text-sm text-muted-foreground">Lite v2</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <SignedOut>
              <SignInButton>
                <Button variant="outline">Sign In</Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="text-center py-16 sm:py-24 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-lg opacity-25 animate-pulse"></div>
              <div className="relative p-4 rounded-full bg-gradient-to-br from-blue-600 to-purple-600">
                <Rocket className="w-12 h-12 text-white" />
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Modern Web Development
            </span>
            <br />
            <span className="text-foreground">Made Simple</span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
            A production-ready Next.js starter with authentication, database, AI integration, 
            and beautiful UI components. Get from zero to shipped in minutes, not hours.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <SignedOut>
              <SignInButton>
                <Button size="lg" className="btn-gradient btn-hover-glow focus-ring px-8" aria-label="Sign up to get started with CodeGuide Starter Kit">
                  <Sparkles className="w-5 h-5 mr-2" aria-hidden="true" />
                  Get Started Free
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard">
                <Button size="lg" className="btn-gradient btn-hover-glow focus-ring px-8" aria-label="Go to your dashboard">
                  <Sparkles className="w-5 h-5 mr-2" aria-hidden="true" />
                  Go to Dashboard
                </Button>
              </Link>
            </SignedIn>
            
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => setShowSetup(!showSetup)}
              className="focus-ring"
              aria-expanded={showSetup}
              aria-controls="setup-guide"
            >
              <FileText className="w-5 h-5 mr-2" aria-hidden="true" />
              {showSetup ? 'Hide Setup' : 'View Setup Guide'}
            </Button>
            
            <Button size="lg" variant="ghost" asChild className="focus-ring">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                aria-label="View CodeGuide Starter Kit on GitHub (opens in new tab)"
              >
                <Github className="w-5 h-5 mr-2" aria-hidden="true" />
                View on GitHub
              </a>
            </Button>
          </div>

          {/* Environment Status Indicators */}
          <div className="flex flex-wrap justify-center gap-3 sm:gap-4 mb-8" role="status" aria-label="Service status indicators">
            <div className="flex items-center gap-2 px-3 py-2 rounded-full glass transition-all duration-300 hover:scale-105">
              {envStatus.clerk ? (
                <CheckCircle className="w-4 h-4 text-green-500" aria-hidden="true" />
              ) : (
                <Circle className="w-4 h-4 text-gray-400" aria-hidden="true" />
              )}
              <span className="text-sm font-medium">
                Authentication
                <span className="sr-only">
                  {envStatus.clerk ? 'configured' : 'not configured'}
                </span>
              </span>
            </div>
            
            <div className="flex items-center gap-2 px-3 py-2 rounded-full glass transition-all duration-300 hover:scale-105">
              {envStatus.supabase ? (
                <CheckCircle className="w-4 h-4 text-green-500" aria-hidden="true" />
              ) : (
                <Circle className="w-4 h-4 text-gray-400" aria-hidden="true" />
              )}
              <span className="text-sm font-medium">
                Database
                <span className="sr-only">
                  {envStatus.supabase ? 'configured' : 'not configured'}
                </span>
              </span>
            </div>
            
            <div className="flex items-center gap-2 px-3 py-2 rounded-full glass transition-all duration-300 hover:scale-105">
              {envStatus.ai ? (
                <CheckCircle className="w-4 h-4 text-green-500" aria-hidden="true" />
              ) : (
                <Circle className="w-4 h-4 text-gray-400" aria-hidden="true" />
              )}
              <span className="text-sm font-medium">
                AI Integration
                <span className="sr-only">
                  {envStatus.ai ? 'configured' : 'not configured'}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Setup Guide */}
      {showSetup && (
        <section id="setup-guide" className="py-12 px-4" aria-labelledby="setup-heading">
          <SetupGuide envStatus={envStatus} />
        </section>
      )}

      <main className="container mx-auto px-4 sm:px-6 pb-12 max-w-7xl">

        {/* Feature Showcase */}
        <section className="mb-20" aria-labelledby="features-heading">
          <div className="text-center mb-12">
            <h2 id="features-heading" className="text-3xl font-bold mb-4">Everything You Need to Build Fast</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Batteries-included starter kit with all the modern tools and integrations
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8" role="list">
            {/* Authentication */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/20 dark:to-indigo-900/40 animate-fade-in-up animate-delay-100">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 group-hover:from-blue-500 group-hover:to-blue-600 transition-colors">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Authentication</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  Complete user management with Clerk integration
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Sign-up & Sign-in flows</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Protected routes middleware</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>User profile management</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Database */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/40 animate-fade-in-up animate-delay-200">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-green-600 to-green-700 group-hover:from-green-500 group-hover:to-green-600 transition-colors">
                    <Database className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Database</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  Supabase PostgreSQL with real-time capabilities
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Row Level Security</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Real-time subscriptions</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Type-safe queries</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Integration */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-purple-50 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/40 animate-fade-in-up animate-delay-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 group-hover:from-purple-500 group-hover:to-pink-500 transition-colors">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">AI Integration</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  Vercel AI SDK with OpenAI and Claude support
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Streaming chat interface</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Multiple AI providers</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Real-time responses</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* UI Components */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-orange-50 to-red-100 dark:from-orange-900/20 dark:to-red-900/40 animate-fade-in-up animate-delay-400">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-orange-600 to-red-600 group-hover:from-orange-500 group-hover:to-red-500 transition-colors">
                    <Palette className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">UI Components</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  40+ shadcn/ui components with dark mode
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Accessible components</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Dark/light theme toggle</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>TailwindCSS v4</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* TypeScript */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-cyan-50 to-blue-100 dark:from-cyan-900/20 dark:to-blue-900/40 animate-fade-in-up animate-delay-500">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-600 group-hover:from-cyan-500 group-hover:to-blue-500 transition-colors">
                    <Code2 className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">TypeScript</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  Type-safe development with strict mode
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Strict mode enabled</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Path aliases configured</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Type-safe API routes</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Developer Experience */}
            <Card role="listitem" className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-0 bg-gradient-to-br from-yellow-50 to-orange-100 dark:from-yellow-900/20 dark:to-orange-900/40 animate-fade-in-up animate-delay-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-yellow-600 to-orange-600 group-hover:from-yellow-500 group-hover:to-orange-500 transition-colors">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Developer Experience</CardTitle>
                </div>
                <p className="text-muted-foreground">
                  Optimized for productivity and maintainability
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Hot reload & fast refresh</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>ESLint & Prettier</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Docker dev container</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* AI Chat Demo */}
        <SignedIn>
          <section className="mb-20" aria-labelledby="chat-demo-heading">
            <div className="text-center mb-8">
              <h2 id="chat-demo-heading" className="text-3xl font-bold mb-4">Try the AI Chat</h2>
              <p className="text-xl text-muted-foreground">
                Experience the integrated AI chat powered by Vercel AI SDK
              </p>
            </div>
            
            <div className="max-w-4xl mx-auto">
              <Card className="p-4 sm:p-6 glass-card" role="region" aria-label="AI Chat Interface">
                <Chat />
              </Card>
            </div>
          </section>
        </SignedIn>

        {/* Quick Start Section */}
        <section className="text-center py-16" aria-labelledby="quick-start-heading">
          <h2 id="quick-start-heading" className="text-3xl font-bold mb-4">Ready to Build Something Amazing?</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Clone the repository, add your environment variables, and start building your next project in minutes.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild className="btn-gradient btn-hover-glow focus-ring px-8">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                aria-label="Clone CodeGuide Starter Kit repository on GitHub (opens in new tab)"
              >
                <Github className="w-5 h-5 mr-2" aria-hidden="true" />
                Clone Repository
              </a>
            </Button>
            
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => setShowSetup(true)}
              className="focus-ring"
              aria-label="View setup instructions"
            >
              <FileText className="w-5 h-5 mr-2" aria-hidden="true" />
              Setup Instructions
            </Button>
          </div>
        </section>

      </main>
      
      {/* Footer */}
      <footer className="border-t bg-muted/50 py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold">CodeGuide Starter Kit Lite v2</span>
          </div>
          
          <p className="text-muted-foreground mb-4">
            Built with Next.js, TypeScript, Tailwind CSS, shadcn/ui, Clerk, Supabase, and Vercel AI SDK
          </p>
          
          <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground transition-colors">
              Documentation
            </a>
            <a href="#" className="hover:text-foreground transition-colors">
              GitHub
            </a>
            <a href="#" className="hover:text-foreground transition-colors">
              Examples
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
