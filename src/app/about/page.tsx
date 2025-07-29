"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { ArrowLeft, Github, ExternalLink, Heart, Code2, Zap, Shield, Database } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="relative px-4 py-6">
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
              <UserButton />
            </SignedIn>
          </div>
        </div>

        <div className="absolute top-4 left-4 sm:top-6 sm:left-6">
          <Link href="/">
            <Button variant="ghost" size="sm" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>

      <main className="container mx-auto px-4 sm:px-6 pb-12 max-w-4xl">
        {/* Hero Section */}
        <div className="text-center py-8 sm:py-12">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-6">
            <Image
              src="/codeguide-logo.png"
              alt="CodeGuide Logo"
              width={60}
              height={60}
              className="rounded-xl"
            />
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-blue-500 to-blue-400 bg-clip-text text-transparent font-parkinsans">
              About CodeGuide
            </h1>
          </div>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            A modern Next.js starter kit designed to accelerate your development workflow
          </p>
        </div>

        {/* What is CodeGuide */}
        <Card className="p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Code2 className="w-6 h-6 text-blue-500" />
            What is CodeGuide Starter Kit?
          </h2>
          <p className="text-muted-foreground mb-4">
            CodeGuide Starter Kit Lite v2 is a comprehensive Next.js template that provides everything you need to build modern web applications. It combines the latest technologies and best practices to help you start coding immediately without the hassle of initial setup.
          </p>
          <p className="text-muted-foreground">
            Whether you're building a SaaS application, a personal project, or experimenting with new ideas, this starter kit provides a solid foundation with authentication, database integration, AI capabilities, and a beautiful UI component system.
          </p>
        </Card>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="w-6 h-6 text-green-500" />
              <h3 className="text-xl font-semibold">Authentication Ready</h3>
            </div>
            <p className="text-muted-foreground">
              Integrated with Clerk for secure, scalable authentication. Supports social logins, user management, and protected routes out of the box.
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <Database className="w-6 h-6 text-blue-500" />
              <h3 className="text-xl font-semibold">Database Integration</h3>
            </div>
            <p className="text-muted-foreground">
              Connected to Supabase with Row Level Security (RLS) policies. Includes example schemas and migration files to get you started.
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <Zap className="w-6 h-6 text-purple-500" />
              <h3 className="text-xl font-semibold">AI-Powered</h3>
            </div>
            <p className="text-muted-foreground">
              Built-in chat interface powered by Vercel AI SDK. Supports both OpenAI and Anthropic Claude models for AI-driven features.
            </p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <Heart className="w-6 h-6 text-red-500" />
              <h3 className="text-xl font-semibold">Beautiful UI</h3>
            </div>
            <p className="text-muted-foreground">
              40+ shadcn/ui components with dark mode support. Styled with TailwindCSS v4 and includes theme customization.
            </p>
          </Card>
        </div>

        {/* Tech Stack */}
        <Card className="p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Tech Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">Next.js 15</div>
              <div className="text-xs text-muted-foreground">App Router</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">TypeScript</div>
              <div className="text-xs text-muted-foreground">Strict Mode</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">TailwindCSS</div>
              <div className="text-xs text-muted-foreground">v4 + Dark Mode</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">shadcn/ui</div>
              <div className="text-xs text-muted-foreground">40+ Components</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">Clerk</div>
              <div className="text-xs text-muted-foreground">Authentication</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-muted/30">
              <div className="font-semibold text-sm">Supabase</div>
              <div className="text-xs text-muted-foreground">Database + RLS</div>
            </div>
          </div>
        </Card>

        {/* Getting Started */}
        <Card className="p-6">
          <h2 className="text-2xl font-bold mb-4">Getting Started</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold mt-0.5">1</div>
              <div>
                <div className="font-semibold">Clone and Install</div>
                <div className="text-sm text-muted-foreground">Get the starter kit and install dependencies</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold mt-0.5">2</div>
              <div>
                <div className="font-semibold">Configure Services</div>
                <div className="text-sm text-muted-foreground">Set up Clerk authentication and Supabase database</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold mt-0.5">3</div>
              <div>
                <div className="font-semibold">Start Building</div>
                <div className="text-sm text-muted-foreground">Add your features and customize the design</div>
              </div>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}