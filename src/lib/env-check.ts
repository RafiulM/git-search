export function checkEnvironmentVariables() {
  const requiredEnvVars = {
    clerk: {
      publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
      secretKey: process.env.CLERK_SECRET_KEY,
    },
    supabase: {
      url: process.env.NEXT_PUBLIC_SUPABASE_URL,
      anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    },
    ai: {
      openai: process.env.OPENAI_API_KEY,
      anthropic: process.env.ANTHROPIC_API_KEY,
    },
  };

  const status = {
    clerk: !!(
      requiredEnvVars.clerk.publishableKey && requiredEnvVars.clerk.secretKey
    ),
    supabase: !!(
      requiredEnvVars.supabase.url && requiredEnvVars.supabase.anonKey
    ),
    ai: !!(requiredEnvVars.ai.openai || requiredEnvVars.ai.anthropic),
    allConfigured: false,
  };

  status.allConfigured = status.clerk && status.supabase && status.ai;

  return status;
}

export function getSetupInstructions() {
  return [
    {
      service: "Clerk",
      description: "Authentication service for user management",
      steps: [
        "Go to https://dashboard.clerk.com/",
        "Create a new application",
        "Copy NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to .env.local",
      ],
      envVars: ["NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY"],
    },
    {
      service: "Supabase",
      description: "Database and real-time subscriptions",
      steps: [
        "Go to https://supabase.com/dashboard",
        "Create a new project",
        "Copy NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to .env.local",
      ],
      envVars: ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY"],
    },
    {
      service: "OpenAI",
      description: "AI language model for chat functionality",
      steps: [
        "Go to https://platform.openai.com/",
        "Create an API key",
        "Copy OPENAI_API_KEY to .env.local",
      ],
      envVars: ["OPENAI_API_KEY"],
    },
  ];
}
