[![Git-Search](/codeguide-backdrop.svg)](#)

# Git-Search Monorepo

A modern monorepo containing the Git-Search application stack with Next.js frontend and FastAPI backend.

## Structure

```
├── apps/
│   ├── web/          # Next.js frontend application
│   └── api/          # FastAPI backend application
├── packages/         # Shared packages (future use)
└── documentation/    # Project documentation
```

## Tech Stack

### Frontend (`apps/web`)
- **Framework:** [Next.js 15](https://nextjs.org/) (App Router)
- **Language:** TypeScript
- **Authentication:** [Clerk](https://clerk.com/)
- **Database:** [Supabase](https://supabase.com/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Components:** [shadcn/ui](https://ui.shadcn.com/)
- **AI Integration:** [Vercel AI SDK](https://sdk.vercel.ai/)
- **Theme System:** [next-themes](https://github.com/pacocoursey/next-themes)

### Backend (`apps/api`)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Language:** Python 3.8+
- **Database:** [Supabase](https://supabase.com/) / PostgreSQL
- **Authentication:** JWT with integration to Clerk
- **Validation:** [Pydantic](https://pydantic.dev/)

## Prerequisites

Before you begin, ensure you have the following:
- Node.js 18+ and npm
- Python 3.8+ and pip
- A [Clerk](https://clerk.com/) account for authentication
- A [Supabase](https://supabase.com/) account for database
- Optional: [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/) API key for AI features
- Generated project documents for best development experience

## Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd git-search-monorepo
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

### Development

3. **Start the web application**
   ```bash
   npm run dev:web
   ```
   The web app will be available at http://localhost:3000

4. **Start the API server** (in a new terminal)
   ```bash
   npm run dev:api
   ```
   The API will be available at http://localhost:8000

### Environment Configuration

5. **Web app environment variables**
   ```bash
   cp apps/web/.env.example apps/web/.env.local
   # Edit apps/web/.env.local with your values
   ```

6. **API environment variables**
   ```bash
   cp apps/api/.env.example apps/api/.env
   # Edit apps/api/.env with your values
   ```

### Available Scripts

- `npm run dev` - Start the web application (default)
- `npm run dev:web` - Start the Next.js web application
- `npm run dev:api` - Start the FastAPI backend
- `npm run build` - Build the web application
- `npm run build:web` - Build the Next.js application  
- `npm run build:api` - Build the FastAPI application
- `npm run lint` - Run ESLint on the web application
- `npm run type-check` - Run TypeScript type checking

## Configuration

### Clerk Setup
1. Go to [Clerk Dashboard](https://dashboard.clerk.com/)
2. Create a new application
3. Go to API Keys
4. Copy the `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`

### Supabase Setup
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to Authentication → Integrations → Add Clerk (for third-party auth)
4. Go to Project Settings > API
5. Copy the `Project URL` as `NEXT_PUBLIC_SUPABASE_URL`
6. Copy the `anon` public key as `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### AI Integration Setup (Optional)
1. Go to [OpenAI Platform](https://platform.openai.com/) or [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Add to your environment variables

## Environment Variables

Create a `.env.local` file in the root directory with the following variables:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key
CLERK_SECRET_KEY=your_secret_key

# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# AI Integration (Optional)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Features

- 🔐 Authentication with Clerk (middleware protection)
- 🗄️ Supabase Database with third-party auth integration
- 🤖 AI Chat Interface with OpenAI/Anthropic support
- 🎨 40+ shadcn/ui components (New York style)
- 🌙 Dark mode with system preference detection
- 🎯 Built-in setup dashboard with service status
- 🚀 App Router with Server Components
- 🔒 Row Level Security examples with Clerk user IDs
- 📱 Responsive design with TailwindCSS v4
- 🎨 Custom fonts (Geist Sans, Geist Mono, Parkinsans)

## Project Structure

```
git-search-monorepo/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── api/chat/          # AI chat API endpoint
│   │   ├── globals.css        # Global styles with dark mode
│   │   ├── layout.tsx         # Root layout with providers
│   │   └── page.tsx           # Hero + setup dashboard
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui components (40+)
│   │   ├── chat.tsx           # AI chat interface
│   │   ├── theme-provider.tsx # Theme context
│   │   └── theme-toggle.tsx   # Dark mode toggle
│   ├── lib/                   # Utility functions
│   │   ├── supabase.ts        # Supabase client with Clerk auth
│   │   ├── user.ts            # User utilities
│   │   ├── utils.ts           # General utilities
│   │   └── env-check.ts       # Environment validation
│   └── middleware.ts          # Clerk route protection
├── supabase/
│   └── migrations/            # Database migrations with RLS examples
├── CLAUDE.md                  # AI coding agent documentation
├── SUPABASE_CLERK_SETUP.md   # Integration setup guide
└── components.json            # shadcn/ui configuration
```

## Database Integration

This starter includes modern Clerk + Supabase integration:

- **Third-party auth** (not deprecated JWT templates)
- **Row Level Security** policies using `auth.jwt() ->> 'sub'` for Clerk user IDs
- **Example migrations** with various RLS patterns (user-owned, public/private, collaboration)
- **Server-side client** with automatic Clerk token handling

## AI Coding Agent Integration

This project is optimized for development:

- **`CLAUDE.md`** - Comprehensive project context and patterns
- **Setup guides** with detailed integration steps
- **Example migrations** with RLS policy templates
- **Clear file structure** and naming conventions
- **TypeScript integration** with proper type definitions

## Documentation Setup

Project documentation is available in the `documentation/` directory:

```bash
# Example structure
documentation/
├── project_requirements_document.md             
├── app_flow_document.md
├── frontend_guideline_document.md
└── backend_structure_document.md
```

These documentation files can be used as a reference for your project's features and implementation details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.