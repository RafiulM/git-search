"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import Chat from "@/components/chat";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { checkEnvironmentVariables } from "@/lib/env-check";
import {
  Copy,
  CheckCircle,
  AlertCircle,
  Zap,
  Database,
  Shield,
  ExternalLink,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Image from "next/image";

export default function Home() {
  const envStatus = checkEnvironmentVariables();

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
              <UserButton />
            </SignedIn>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-4">
          <Image
            src="/codeguide-logo.png"
            alt="CodeGuide Logo"
            width={50}
            height={50}
            className="rounded-xl sm:w-[60px] sm:h-[60px]"
          />
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 via-blue-500 to-blue-400 bg-clip-text text-transparent font-parkinsans">
            CodeGuide Starter
          </h1>
        </div>
        <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto px-4">
          Build faster with your AI coding agent
        </p>
      </div>

      <main className="container mx-auto px-4 sm:px-6 pb-12 sm:pb-8 max-w-5xl">
        {envStatus.allConfigured ? (
          <div className="text-center mb-8">
            <div className="text-4xl sm:text-5xl mb-2">🎉</div>
            <div className="font-bold text-lg sm:text-xl mb-1">All Set!</div>
            <div className="text-sm sm:text-base text-muted-foreground">
              Ready for development
            </div>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl sm:text-5xl mb-2">⚠️</div>
              <div className="font-semibold text-lg sm:text-xl mb-1">
                Setup Required
              </div>
              <div className="text-sm sm:text-base text-muted-foreground">
                Retrieve keys for environment variables
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              {/* Clerk */}
              <div className="text-center p-3 sm:p-4 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10">
                <div className="flex justify-center mb-3">
                  {envStatus.clerk ? (
                    <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-green-500" />
                  ) : (
                    <Shield className="w-6 h-6 sm:w-8 sm:h-8 text-blue-500" />
                  )}
                </div>
                <div className="font-semibold mb-2 text-sm sm:text-base">
                  Clerk Auth
                </div>
                <div className="text-xs text-muted-foreground mb-3">
                  {envStatus.clerk ? "✓ Ready" : "Setup required"}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    window.open("https://dashboard.clerk.com", "_blank")
                  }
                  className="w-full text-xs sm:text-sm"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Dashboard
                </Button>
              </div>

              {/* Supabase */}
              <div className="text-center p-3 sm:p-4 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10">
                <div className="flex justify-center mb-3">
                  {envStatus.supabase ? (
                    <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-green-500" />
                  ) : (
                    <Database className="w-6 h-6 sm:w-8 sm:h-8 text-green-500" />
                  )}
                </div>
                <div className="font-semibold mb-2 text-sm sm:text-base">
                  Supabase DB
                </div>
                <div className="text-xs text-muted-foreground mb-3">
                  {envStatus.supabase ? "✓ Ready" : "Setup required"}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    window.open("https://supabase.com/dashboard", "_blank")
                  }
                  className="w-full text-xs sm:text-sm"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Dashboard
                </Button>
              </div>

              {/* AI */}
              <div className="text-center p-3 sm:p-4 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 sm:col-span-2 md:col-span-1">
                <div className="flex justify-center mb-3">
                  {envStatus.ai ? (
                    <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-green-500" />
                  ) : (
                    <Zap className="w-6 h-6 sm:w-8 sm:h-8 text-purple-500" />
                  )}
                </div>
                <div className="font-semibold mb-2 text-sm sm:text-base">
                  AI SDK
                </div>
                <div className="text-xs text-muted-foreground mb-3">
                  {envStatus.ai ? "✓ Ready" : "Optional"}
                </div>
                <div className="grid grid-cols-2 gap-1 sm:gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      window.open("https://platform.openai.com", "_blank")
                    }
                    className="text-xs px-1 sm:px-2"
                  >
                    OpenAI
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      window.open("https://console.anthropic.com", "_blank")
                    }
                    className="text-xs px-1 sm:px-2"
                  >
                    Anthropic
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Chat Section */}
        <SignedIn>
          {envStatus.allConfigured && (
            <div className="mt-6 sm:mt-8">
              <Chat />
            </div>
          )}
        </SignedIn>
      </main>
    </div>
  );
}
