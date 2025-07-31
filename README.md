# CodeGuide Starter Kit Lite v2

<div align="center">

🚀 **A modern Next.js starter template with authentication, database integration, AI capabilities, and comprehensive UI components**

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

CodeGuide Starter Kit Lite v2 is a comprehensive Next.js starter template that accelerates your development workflow. It comes pre-configured with modern authentication, database integration, AI capabilities, and a complete UI component system to help you build production-ready applications faster.

## 📸 Demo

> **Note**: Screenshots and live demo links will be added once deployed.

### Key Features Showcase
- 🏠 **Dashboard**: Clean setup status and environment validation
- 💬 **AI Chat**: Interactive AI conversation interface
- 🎨 **UI Components**: 40+ pre-built shadcn/ui components
- 🌙 **Theme System**: Seamless dark/light mode switching

## ✨ Features

- 🔐 **Authentication Ready** - Pre-configured Clerk authentication with middleware protection
- 🗄️ **Database Integration** - Supabase setup with Row Level Security (RLS) policies
- 🤖 **AI Integration** - Vercel AI SDK with OpenAI and Anthropic support
- 🎨 **Complete UI System** - 40+ shadcn/ui components (New York style)
- 🌙 **Theme System** - Dark/light mode with next-themes and system detection
- 📱 **Responsive Design** - Mobile-first design with TailwindCSS v4
- ⚡ **Performance Optimized** - Next.js 15 App Router with TypeScript
- 🔧 **Developer Experience** - ESLint, TypeScript strict mode, and hot reloading

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
- Optional: [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/) API key for AI features

## ⚙️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/RafiulM/codeguide-starter-kit-lite-v2.git
   cd codeguide-starter-kit-lite-v2
   ```

2. **Verify Node.js version**
   ```bash
   node --version  # Should be 18.0.0 or higher
   npm --version   # Should be 8.0.0 or higher
   ```

3. **Install dependencies**
   ```bash
   # Using npm (recommended)
   npm install

   # Or using yarn
   yarn install

   # Or using pnpm
   pnpm install
   ```

4. **Environment Variables Setup**
   ```bash
   # Copy the example environment file
   cp .env.example .env.local

   # Edit the .env.local file with your actual values
   # See the Configuration section below for detailed setup
   ```

5. **Database Setup** (Optional for basic functionality)
   ```bash
   # Install Supabase CLI if not already installed
   npm install -g supabase

   # Initialize Supabase (if needed)
   supabase init

   # Run database migrations
   npx supabase db push
   ```

6. **Start the development server**
   ```bash
   npm run dev
   ```

7. **Verify installation**
   - Open [http://localhost:3000](http://localhost:3000)
   - You should see the Git Search application
   - Check the browser console for any errors

### Installation Troubleshooting

If you encounter issues during installation:

1. **Node.js version issues**:
   ```bash
   # Use nvm to install the correct version
   nvm install 18
   nvm use 18
   ```

2. **Dependency conflicts**:
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Permission errors** (macOS/Linux):
   ```bash
   # Fix npm permissions
   sudo chown -R $(whoami) ~/.npm
   ```

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

#### 3. AI Integration Setup (Optional)
1. Sign up for [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/)
2. Generate an API key
3. Add to your environment variables for AI-powered summaries

## 🏗️ Project Structure

```
codeguide-starter-kit-lite-v2/
├── src/
│   ├── app/                    # Next.js app router
│   │   ├── api/               # API routes
│   │   │   └── chat/          # AI chat endpoint
│   │   ├── globals.css        # Global styles with dark mode
│   │   ├── layout.tsx         # Root layout with providers
│   │   └── page.tsx           # Home page with status dashboard
│   ├── components/            # React components
│   │   ├── ui/                # shadcn/ui components (40+ components)
│   │   ├── chat.tsx           # AI chat interface
│   │   ├── setup-guide.tsx    # Configuration guide
│   │   ├── theme-provider.tsx # Theme context provider
│   │   └── theme-toggle.tsx   # Dark mode toggle components
│   ├── lib/                   # Utility functions
│   │   ├── utils.ts           # Utility functions (cn, etc.)
│   │   ├── supabase.ts        # Supabase client configurations
│   │   ├── user.ts            # User utilities using Clerk
│   │   └── env-check.ts       # Environment validation
│   └── middleware.ts          # Clerk authentication middleware
├── supabase/
│   └── migrations/            # Database migrations
├── components.json            # shadcn/ui configuration
├── CLAUDE.md                  # AI assistant context
├── CONTRIBUTING.md            # Contribution guidelines
├── SUPABASE_CLERK_SETUP.md   # Integration setup guide
└── public/                   # Static assets
```

## 🎯 Usage

### Getting Started
1. **Setup Environment**: Follow the installation steps above
2. **Run the Application**: Start the development server with `npm run dev`
3. **Check Status**: Visit `http://localhost:3000` to see setup status
4. **Configure Services**: Use the dashboard links to set up Clerk, Supabase, and AI services

### AI Chat Interface
1. **Sign In**: Authenticate with Clerk to access AI features
2. **Start Chatting**: Use the integrated chat interface to interact with AI
3. **Ask Questions**: Get help with development, coding, or project setup

### Building Your Application
- **Authentication**: Routes are automatically protected with Clerk middleware
- **Database**: Use the pre-configured Supabase client with RLS policies
- **UI Components**: Leverage 40+ shadcn/ui components
- **Styling**: Customize themes and styles with TailwindCSS v4
- **AI Integration**: Add AI features using the Vercel AI SDK

## 🔌 API Documentation

The starter kit provides a foundation for building API endpoints. Currently included:

### Authentication

All API endpoints can use Clerk authentication. Include the authorization header:

```bash
Authorization: Bearer <clerk-session-token>
```

### Available Endpoints

#### AI Chat Integration
```http
POST /api/chat
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Help me understand Next.js App Router"
    }
  ]
}
```

**Response:**
- Streaming AI response using Vercel AI SDK
- Supports both OpenAI and Anthropic models
- Requires authentication via Clerk

### Extending the API

The starter kit provides patterns for adding your own API endpoints:

1. **Create API Routes**: Add files to `src/app/api/`
2. **Authentication**: Use Clerk's `auth()` helper for protected routes
3. **Database Integration**: Use the pre-configured Supabase client
4. **Type Safety**: Leverage TypeScript for request/response types

**Example API Route:**
```typescript
// src/app/api/users/route.ts
import { auth } from '@clerk/nextjs'
import { createSupabaseServerClient } from '@/lib/supabase'

export async function GET() {
  const { userId } = auth()
  if (!userId) {
    return new Response('Unauthorized', { status: 401 })
  }
  
  const supabase = await createSupabaseServerClient()
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', userId)
  
  return Response.json({ data, error })
}
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Authentication Issues

**Problem**: Clerk authentication not working
```bash
Error: Clerk: Missing publishable key
```

**Solution**:
1. Verify your Clerk keys in `.env.local`
2. Ensure keys start with the correct prefixes:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_test_` or `pk_live_`
   - `CLERK_SECRET_KEY` starts with `sk_test_` or `sk_live_`
3. Restart your development server after adding keys

**Problem**: Redirects not working after authentication
**Solution**:
1. Check your Clerk dashboard settings
2. Add your domain to allowed redirect URLs
3. For local development, include `http://localhost:3000`

#### Database Issues

**Problem**: Supabase connection failed
```bash
Error: Invalid Supabase URL or anon key
```

**Solution**:
1. Verify your Supabase project URL and anon key
2. Check if your Supabase project is active
3. Ensure RLS (Row Level Security) policies are properly configured
4. Test connection with the Supabase dashboard

**Problem**: Database migrations not working
```bash
Error: relation "posts" does not exist
```

**Solution**:
```bash
# Reset and re-run migrations
supabase db reset
npx supabase db push
```

#### API Issues

**Problem**: GitHub API rate limiting
```bash
Error: API rate limit exceeded
```

**Solution**:
1. Ensure you have a valid GitHub token in your environment variables
2. Use a personal access token for higher rate limits
3. Implement caching for frequently accessed data
4. Consider implementing retry logic with exponential backoff

**Problem**: AI features not working
```bash
Error: OpenAI API key invalid
```

**Solution**:
1. Verify your API key is correct and active
2. Check your API usage limits and billing
3. Ensure the API key has the necessary permissions
4. Try switching between OpenAI and Anthropic providers

#### Build and Development Issues

**Problem**: Next.js build fails
```bash
Error: Type error in components
```

**Solution**:
```bash
# Check TypeScript errors
npm run lint
npx tsc --noEmit

# Clear Next.js cache
rm -rf .next
npm run dev
```

**Problem**: Styling issues with Tailwind CSS
**Solution**:
1. Ensure Tailwind CSS is properly configured
2. Check if PostCSS config is correct
3. Verify `globals.css` imports
4. Clear browser cache and restart development server

#### Performance Issues

**Problem**: Slow search results
**Solution**:
1. Implement search result caching
2. Add pagination to limit results per page
3. Use debouncing for search input
4. Optimize API calls with proper error handling

**Problem**: Large bundle size
**Solution**:
```bash
# Analyze bundle size
npm install -g @next/bundle-analyzer
ANALYZE=true npm run build
```

### Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look at browser console and terminal output
2. **Search existing issues**: Check [GitHub Issues](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/issues)
3. **Create a new issue**: Include error messages, steps to reproduce, and environment details
4. **Join discussions**: Participate in [GitHub Discussions](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/discussions)

### Debug Mode

Enable debug mode for more detailed logging:

```bash
# Add to your .env.local
DEBUG=true
NODE_ENV=development
```

## 🤝 Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit pull requests, report issues, and contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Performance & Deployment

### Performance Optimizations

Git Search is built with performance in mind:

- **Server-Side Rendering (SSR)**: Fast initial page loads with Next.js App Router
- **Static Generation**: Pre-built pages for better SEO and performance
- **Image Optimization**: Automatic image compression and lazy loading
- **Code Splitting**: Automatic bundle splitting for faster loading
- **Caching Strategy**: Redis/in-memory caching for API responses
- **Database Optimization**: Efficient queries with proper indexing

### Deployment Options

#### Vercel (Recommended)

1. **Connect your repository**:
   - Fork this repository
   - Connect to Vercel dashboard
   - Import your forked repository

2. **Environment Variables**:
   - Add all required environment variables in Vercel dashboard
   - Use production values for Clerk, Supabase, and API keys

3. **Deploy**:
   ```bash
   # Automatic deployment on every push to main branch
   git push origin main
   ```

#### Docker Deployment

```dockerfile
# Dockerfile included in repository
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**Build and run**:
```bash
docker build -t codeguide-starter .
docker run -p 3000:3000 --env-file .env.local codeguide-starter
```

#### Self-Hosted Deployment

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Start production server**:
   ```bash
   npm start
   ```

3. **Process Manager (PM2)**:
   ```bash
   npm install -g pm2
   pm2 start npm --name "codeguide-starter" -- start
   pm2 save
   pm2 startup
   ```

### Environment-Specific Configuration

#### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Use production API keys (Clerk, Supabase, etc.)
- [ ] Enable HTTPS
- [ ] Configure proper CORS settings
- [ ] Set up monitoring and logging
- [ ] Configure database backups
- [ ] Set up CI/CD pipeline
- [ ] Enable rate limiting
- [ ] Configure CDN for static assets

#### Security Considerations

- Use environment variables for all sensitive data
- Enable HTTPS in production
- Configure proper CORS policies
- Implement rate limiting
- Regular security updates
- Monitor for vulnerabilities

### Monitoring and Analytics

Recommended tools for production monitoring:

- **Performance**: Vercel Analytics, Google PageSpeed Insights
- **Error Tracking**: Sentry, LogRocket
- **Uptime Monitoring**: Pingdom, UptimeRobot
- **User Analytics**: Plausible, Google Analytics

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/) and [React](https://reactjs.org/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Authentication by [Clerk](https://clerk.com/)
- Database powered by [Supabase](https://supabase.com/)
- AI capabilities by [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/)

## 📞 Support & Community

### Get Help

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/wiki)
- 💡 **Feature Requests**: [Enhancement Issues](https://github.com/RafiulM/codeguide-starter-kit-lite-v2/issues/new?template=feature_request.md)

### Connect with the Community

- 🌟 **Star the repo** if you find it useful
- 🍴 **Fork** to contribute your improvements
- 👥 **Follow** [@RafiulM](https://github.com/RafiulM) for updates
- 📱 **Share** with your developer friends

### Support the Project

If Git Search has been helpful to you, consider:

- ⭐ **Starring the repository**
- 🐛 **Reporting bugs** and issues
- 💻 **Contributing code** improvements
- 📝 **Improving documentation**
- 💬 **Helping others** in discussions

---

<div align="center">

**Happy searching! 🔍✨**

*Built with ❤️ by [RafiulM](https://github.com/RafiulM)*

</div>