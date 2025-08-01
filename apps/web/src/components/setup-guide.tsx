"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getSetupInstructions } from "@/lib/env-check";
import { CheckCircle, Circle, ExternalLink, Copy } from "lucide-react";
import { useState } from "react";

interface SetupGuideProps {
  envStatus: {
    clerk: boolean;
    supabase: boolean;
    ai: boolean;
    allConfigured: boolean;
  };
}

export default function SetupGuide({ envStatus }: SetupGuideProps) {
  const [copiedVar, setCopiedVar] = useState<string | null>(null);
  const setupInstructions = getSetupInstructions();

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedVar(text);
      setTimeout(() => setCopiedVar(null), 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  };

  const getServiceStatus = (service: string) => {
    switch (service.toLowerCase()) {
      case "clerk":
        return envStatus.clerk;
      case "supabase":
        return envStatus.supabase;
      case "openai":
        return envStatus.ai;
      default:
        return false;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4">🚀 Setup Your Environment</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Configure these services to unlock the full potential of your starter
          kit
        </p>
      </div>

      <div className="grid gap-6">
        {setupInstructions.map((instruction, index) => {
          const isConfigured = getServiceStatus(instruction.service);

          return (
            <Card
              key={index}
              className="p-6 border-2 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {isConfigured ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : (
                    <Circle className="w-6 h-6 text-gray-400" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-semibold">
                      {instruction.service}
                    </h3>
                    {isConfigured && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                        Configured
                      </span>
                    )}
                  </div>

                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {instruction.description}
                  </p>

                  {!isConfigured && (
                    <>
                      <div className="mb-4">
                        <h4 className="font-medium mb-2">Setup Steps:</h4>
                        <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                          {instruction.steps.map((step, stepIndex) => (
                            <li key={stepIndex}>{step}</li>
                          ))}
                        </ol>
                      </div>

                      <div className="mb-4">
                        <h4 className="font-medium mb-2">
                          Environment Variables:
                        </h4>
                        <div className="space-y-2">
                          {instruction.envVars.map((envVar) => (
                            <div
                              key={envVar}
                              className="flex items-center gap-2"
                            >
                              <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono flex-1">
                                {envVar}=your_value_here
                              </code>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => copyToClipboard(envVar)}
                                className="shrink-0"
                              >
                                {copiedVar === envVar ? (
                                  <CheckCircle className="w-4 h-4" />
                                ) : (
                                  <Copy className="w-4 h-4" />
                                )}
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => {
                          const urls = {
                            Clerk: "https://dashboard.clerk.com/",
                            Supabase: "https://supabase.com/dashboard",
                            OpenAI: "https://platform.openai.com/",
                          };
                          window.open(
                            urls[instruction.service as keyof typeof urls],
                            "_blank",
                          );
                        }}
                      >
                        Open {instruction.service} Dashboard
                        <ExternalLink className="w-4 h-4 ml-2" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {envStatus.allConfigured && (
        <Card className="p-6 border-2 border-green-200 bg-green-50 dark:bg-green-900/20">
          <div className="text-center">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-green-800 dark:text-green-400 mb-2">
              🎉 All Set!
            </h3>
            <p className="text-green-700 dark:text-green-300">
              Your environment is fully configured. The AI chat feature is now
              available!
            </p>
          </div>
        </Card>
      )}

      <Card className="p-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200">
        <h3 className="font-semibold mb-2 text-blue-800 dark:text-blue-400">
          💡 Pro Tip
        </h3>
        <p className="text-sm text-blue-700 dark:text-blue-300">
          After adding your environment variables to{" "}
          <code className="bg-blue-100 dark:bg-blue-800 px-1 py-0.5 rounded">
            .env.local
          </code>
          , restart your development server with{" "}
          <code className="bg-blue-100 dark:bg-blue-800 px-1 py-0.5 rounded">
            npm run dev
          </code>
          for the changes to take effect.
        </p>
      </Card>
    </div>
  );
}
