# Git Search

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-green)](https://supabase.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple)](https://sdk.vercel.ai/)

A powerful search engine that provides GitHub repositories with advanced statistics, AI-generated summaries, and intelligent discovery features. Go beyond basic GitHub search with comprehensive analytics, repository health metrics, and AI-powered insights to discover the perfect repositories for your needs.

## ✨ Features

### 🔍 **Advanced Search & Discovery**
- **Semantic Search**: Find repositories by meaning, not just keywords
- **Multi-Criteria Filtering**: Language, stars, forks, activity, license, size
- **Smart Recommendations**: Discover similar and related repositories
- **Trending Analysis**: Real-time trending repositories and topics
- **Saved Searches**: Bookmark and track your favorite search queries

### 📊 **Comprehensive Repository Analytics**
- **Repository Health Score**: Composite metrics for overall project quality
- **Activity Patterns**: Commit frequency, contributor growth, and development velocity
- **Community Metrics**: Issue response times, maintainer activity, community engagement
- **Code Quality Indicators**: Documentation quality, test coverage insights
- **Dependency Analysis**: Package dependencies and security insights
- **Historical Trends**: Star growth, fork patterns, and popularity evolution

### 🤖 **AI-Powered Insights**
- **Intelligent Summaries**: Auto-generated explanations of what each repository does
- **Technology Stack Analysis**: Detailed breakdown of languages, frameworks, and tools
- **Use Case Identification**: Understand when and why to use a repository
- **Complexity Assessment**: Difficulty levels for contributors and users
- **Architecture Insights**: Project structure and design pattern analysis

### 🎯 **Enhanced User Experience**
- **Personalized Dashboard**: Track repositories, searches, and insights
- **Repository Collections**: Organize repositories into custom lists
- **Comparison Tools**: Side-by-side repository feature comparisons
- **Real-time Updates**: Live statistics and notification system
- **Export & Integration**: Share findings and integrate with development tools

## 🚀 Tech Stack

- **Frontend**: [Next.js 15](https://nextjs.org/) with App Router and React 19
- **Language**: TypeScript with strict mode
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) with dark mode support
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/) (40+ components)
- **Authentication**: [Clerk](https://clerk.com/) with middleware protection
- **Database**: [Supabase](https://supabase.com/) with Row Level Security
- **AI Integration**: [Vercel AI SDK](https://sdk.vercel.ai/) with OpenAI & Anthropic support
- **APIs**: GitHub REST API and GraphQL API
- **Search**: Advanced indexing and semantic search capabilities
- **Theme**: [next-themes](https://github.com/pacocoursey/next-themes) with system preference detection

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** installed
- **GitHub Personal Access Token** for API access
- **[Clerk](https://clerk.com/) account** for authentication
- **[Supabase](https://supabase.com/) account** for database
- **AI API keys** (optional): [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RafiulM/git-search.git
   cd git-search
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env.local
   ```
   
   Fill in your environment variables (see [Configuration](#-configuration) section below)

4. **Database Setup**
   ```bash
   # Run Supabase migrations
   npx supabase db push
   ```

5. **Start the development server**
   ```bash
   npm run dev
   ```

6. **Open [http://localhost:3000](http://localhost:3000)** to see the application

## ⚙️ Configuration

### Required Environment Variables

Create a `.env.local` file with the following variables:

```env
# GitHub API Access
GITHUB_TOKEN=your_github_personal_access_token

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# Supabase Database
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# AI Integration (Optional - for enhanced summaries)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Service Setup Guides

#### GitHub API Setup
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `public_repo` and `read:user` scopes
3. Copy the token to `GITHUB_TOKEN` in your `.env.local`

#### Clerk Authentication Setup
1. Visit [Clerk Dashboard](https://dashboard.clerk.com/)
2. Create a new application
3. Copy the publishable and secret keys from the API Keys section
4. Configure OAuth providers if desired (GitHub, Google, etc.)

#### Supabase Database Setup
1. Create a new project at [Supabase Dashboard](https://supabase.com/dashboard)
2. Go to Settings > API to get your project URL and anon key
3. Follow the [database migration guide](./SUPABASE_SETUP.md) for schema setup

## 🏗️ Project Structure

```
git-search/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API routes
│   │   │   ├── search/        # Repository search endpoints
│   │   │   ├── stats/         # Statistics generation
│   │   │   ├── ai/            # AI summary endpoints
│   │   │   └── github/        # GitHub API integration
│   │   ├── dashboard/         # User dashboard pages
│   │   ├── search/            # Search interface pages
│   │   ├── repository/        # Repository detail pages
│   │   └── profile/           # User profile pages
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── search/            # Search interface components
│   │   ├── repository/        # Repository display components
│   │   ├── analytics/         # Statistics and charts
│   │   └── ai/                # AI summary components
│   ├── lib/
│   │   ├── github.ts          # GitHub API client
│   │   ├── ai.ts              # AI integration utilities
│   │   ├── analytics.ts       # Repository analytics
│   │   ├── search.ts          # Search algorithms
│   │   └── supabase.ts        # Database client
│   └── types/
│       ├── github.ts          # GitHub API types
│       ├── repository.ts      # Repository data types
│       └── analytics.ts       # Analytics types
├── supabase/
│   └── migrations/            # Database schema migrations
├── docs/                      # Additional documentation
└── scripts/                   # Utility scripts
```

## 🎯 Usage

### Basic Repository Search
1. Use the search bar to find repositories by name, description, or topics
2. Apply filters for language, stars, activity level, and more
3. View AI-generated summaries and comprehensive statistics
4. Save interesting repositories to your personal collections

### Advanced Features
- **Semantic Search**: Use natural language queries like "machine learning for beginners"
- **Trend Analysis**: Discover trending repositories in specific technologies
- **Health Scoring**: Evaluate repository quality and maintenance status
- **Comparison Mode**: Compare multiple repositories side-by-side
- **Personal Dashboard**: Track your searches, bookmarks, and insights

### API Endpoints

The application provides RESTful APIs for programmatic access:

- `GET /api/search` - Repository search with filters
- `GET /api/repository/:owner/:name` - Repository details and analytics
- `GET /api/stats/:owner/:name` - Repository statistics
- `POST /api/ai/summarize` - Generate AI repository summary
- `GET /api/trending` - Trending repositories

See [API Documentation](./docs/api.md) for detailed endpoint specifications.

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run end-to-end tests
npm run test:e2e
```

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to [Vercel](https://vercel.com)
2. Configure environment variables in the Vercel dashboard
3. Deploy automatically on every push to main branch

### Docker
```bash
# Build Docker image
docker build -t git-search .

# Run container
docker run -p 3000:3000 --env-file .env.local git-search
```

### Manual Deployment
```bash
# Build the application
npm run build

# Start production server
npm start
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details on:

- Development setup and guidelines
- Code style and standards  
- Testing requirements
- Submitting pull requests
- Reporting issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [GitHub API](https://docs.github.com/en/rest) for repository data
- [Vercel AI SDK](https://sdk.vercel.ai/) for AI integration
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
- [Supabase](https://supabase.com/) for database and authentication
- [Next.js](https://nextjs.org/) for the incredible framework

## 📞 Support

- 📧 **Email**: [support@git-search.dev](mailto:support@git-search.dev)
- 🐛 **Issues**: [GitHub Issues](https://github.com/RafiulM/git-search/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RafiulM/git-search/discussions)
- 📖 **Documentation**: [Full Documentation](./docs/)

---

**Star ⭐ this repository if you find it helpful!**