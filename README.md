# Git Search

🔍 **A powerful search engine for GitHub repositories with enhanced stats and AI-powered summaries**

Git Search is a modern web application that provides an enhanced GitHub repository search experience, offering detailed statistics, AI-generated summaries, and intelligent insights to help developers discover and evaluate repositories more effectively.

## ✨ Features

- 🔍 **Advanced Repository Search** - Search GitHub repositories with enhanced filtering and sorting options
- 📊 **Comprehensive Statistics** - View detailed metrics including stars, forks, issues, and activity trends  
- 🤖 **AI-Powered Summaries** - Get intelligent summaries and insights about repositories using AI
- 🎯 **Smart Recommendations** - Discover related repositories and trending projects
- 🌙 **Dark Mode Support** - Beautiful dark/light theme with system preference detection
- 🔐 **User Authentication** - Secure authentication with personalized search history
- 📱 **Responsive Design** - Optimized for desktop and mobile devices
- ⚡ **Fast Performance** - Built with Next.js 15 and modern web technologies

## 🚀 Tech Stack

- **Framework:** [Next.js 15](https://nextjs.org/) (App Router)
- **Language:** TypeScript
- **Authentication:** [Clerk](https://clerk.com/)
- **Database:** [Supabase](https://supabase.com/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Components:** [shadcn/ui](https://ui.shadcn.com/)
- **AI Integration:** [Vercel AI SDK](https://sdk.vercel.ai/) with OpenAI/Anthropic
- **Theme System:** [next-themes](https://github.com/pacocoursey/next-themes)

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Node.js 18+ installed
- A [Clerk](https://clerk.com/) account for authentication
- A [Supabase](https://supabase.com/) account for database
- A GitHub API token for repository data
- Optional: [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/) API key for AI features

## ⚙️ Installation

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

3. **Environment Variables Setup**
   - Copy the `.env.example` file to `.env.local`:
     ```bash
     cp .env.example .env.local
     ```
   - Fill in the environment variables in `.env.local` (see Configuration section below)

4. **Set up the database**
   ```bash
   # Run Supabase migrations
   npx supabase db push
   ```

5. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

6. **Open [http://localhost:3000](http://localhost:3000) to view the application**

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory with the following variables:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Supabase Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# GitHub API
GITHUB_TOKEN=ghp_...

# AI Integration (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Service Setup

#### 1. Clerk Setup
1. Go to [Clerk Dashboard](https://dashboard.clerk.com/)
2. Create a new application
3. Go to API Keys and copy your keys
4. Configure the allowed redirect URLs for your domain

#### 2. Supabase Setup
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to Authentication → Integrations → Add Clerk (for third-party auth)
4. Copy your project URL and anon key from Project Settings → API

#### 3. GitHub API Setup
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create a new token with appropriate permissions for repository access
3. Add the token to your environment variables

#### 4. AI Integration Setup (Optional)
1. Sign up for [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/)
2. Generate an API key
3. Add to your environment variables for AI-powered summaries

## 🏗️ Project Structure

```
git-search/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── api/               # API routes
│   │   │   ├── chat/          # AI chat endpoint
│   │   │   ├── search/        # GitHub search API
│   │   │   └── repos/         # Repository data API
│   │   ├── search/            # Search results page
│   │   ├── repo/              # Repository detail page
│   │   ├── globals.css        # Global styles
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── search/            # Search-related components
│   │   ├── repo/              # Repository components
│   │   ├── chat.tsx           # AI chat interface
│   │   └── theme-toggle.tsx   # Dark mode toggle
│   ├── lib/                   # Utility functions
│   │   ├── github.ts          # GitHub API integration
│   │   ├── supabase.ts        # Database client
│   │   ├── ai.ts              # AI integration utilities
│   │   └── utils.ts           # General utilities
│   └── types/                 # TypeScript type definitions
├── supabase/
│   └── migrations/            # Database migrations
├── docs/                      # Documentation
└── public/                    # Static assets
```

## 🎯 Usage

### Basic Search
1. Navigate to the home page
2. Enter search terms in the search bar
3. Use filters to refine results (language, stars, last updated, etc.)
4. Click on repositories to view detailed information

### AI Summaries
1. View any repository detail page
2. Click "Generate AI Summary" to get intelligent insights
3. Ask questions about the repository using the AI chat interface

### Advanced Features
- **Search History**: View your recent searches (requires authentication)
- **Favorites**: Save repositories for later reference
- **Custom Filters**: Create and save custom search filters
- **Export Data**: Export search results and statistics

## 🤝 Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit pull requests, report issues, and contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/) and [React](https://reactjs.org/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Authentication by [Clerk](https://clerk.com/)
- Database powered by [Supabase](https://supabase.com/)
- AI capabilities by [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/RafiulM/git-search/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RafiulM/git-search/discussions)
- 📧 **Email**: [your-email@example.com](mailto:your-email@example.com)

---

**Happy searching! 🔍✨**