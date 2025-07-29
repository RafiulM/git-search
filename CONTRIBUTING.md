# Contributing to Git Search

Thank you for your interest in contributing to Git Search! We welcome contributions from everyone, whether you're fixing bugs, adding features, improving documentation, or helping with community support.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Project Architecture](#-project-architecture)
- [Contributing Guidelines](#-contributing-guidelines)
- [Development Workflow](#-development-workflow)
- [Code Standards](#-code-standards)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Community](#-community)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@git-search.dev](mailto:conduct@git-search.dev).

### Our Standards

- **Be respectful** and inclusive in all interactions
- **Be constructive** when giving feedback
- **Focus on what is best** for the community and project
- **Show empathy** towards other community members
- **Learn from mistakes** and help others learn too

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Node.js 18+** and npm/yarn/pnpm
- **Git** for version control
- **GitHub account** for pull requests
- **Basic knowledge** of TypeScript, React, and Next.js
- **Understanding** of the project's purpose and architecture

### Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/git-search.git
   cd git-search
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/RafiulM/git-search.git
   ```
4. **Follow the setup instructions** in the [README.md](./README.md)

## 🛠️ Development Setup

### Environment Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env.local
   ```

2. **Set up required services**:
   - GitHub Personal Access Token
   - Clerk authentication (for auth features)
   - Supabase database (for data persistence)
   - AI API keys (optional, for AI features)

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Run database migrations**:
   ```bash
   npx supabase db push
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

### Development Commands

```bash
# Development
npm run dev          # Start dev server with hot reload
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run type-check   # Run TypeScript checks

# Testing
npm test             # Run all tests
npm run test:watch   # Run tests in watch mode
npm run test:e2e     # Run end-to-end tests
npm run test:coverage # Generate coverage report

# Database
npm run db:reset     # Reset local database
npm run db:seed      # Seed database with sample data
npm run db:migrate   # Run pending migrations
```

## 🏗️ Project Architecture

### Core Components

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API endpoints
│   │   ├── search/        # Repository search logic
│   │   ├── stats/         # Analytics generation
│   │   ├── ai/            # AI summary services
│   │   └── github/        # GitHub API integration
│   ├── (routes)/          # Application pages
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # shadcn/ui base components
│   ├── search/            # Search interface components
│   ├── repository/        # Repository display components
│   ├── analytics/         # Charts and statistics
│   └── layout/            # Layout components
├── lib/
│   ├── github.ts          # GitHub API client
│   ├── ai.ts              # AI service integration
│   ├── analytics.ts       # Repository analytics
│   ├── search.ts          # Search algorithms
│   └── database.ts        # Database utilities
└── types/                 # TypeScript type definitions
```

### Key Technologies

- **Next.js 15**: App Router, Server Components, API Routes
- **TypeScript**: Strict type checking and inference
- **Tailwind CSS**: Utility-first styling with custom components
- **shadcn/ui**: High-quality, accessible UI components
- **Supabase**: PostgreSQL database with real-time features
- **Clerk**: Authentication and user management
- **GitHub API**: Repository data and statistics
- **AI SDK**: OpenAI/Anthropic integration for summaries

## 🎯 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

#### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Add screenshots/videos if helpful
- Specify environment details

#### ✨ Feature Requests
- Use the feature request template
- Explain the use case and benefits
- Provide mockups or examples if possible
- Consider implementation complexity

#### 🔧 Code Contributions
- Bug fixes
- Feature implementations
- Performance improvements
- Code refactoring
- Test coverage improvements

#### 📚 Documentation
- README improvements
- Code comments and docstrings
- API documentation
- Tutorial content
- Translation support

#### 🎨 Design & UX
- UI/UX improvements
- Accessibility enhancements
- Mobile responsiveness
- Design system contributions

### Areas We Need Help

#### High Priority
- **Search Algorithm Improvements**: Better ranking and relevance
- **Performance Optimization**: Faster search and data loading
- **Mobile Experience**: Responsive design improvements
- **Accessibility**: ARIA labels, keyboard navigation
- **Test Coverage**: Unit and integration tests

#### Medium Priority
- **AI Summary Quality**: Better repository analysis
- **Data Visualization**: Enhanced charts and statistics
- **User Experience**: Onboarding and feature discovery
- **API Documentation**: Comprehensive endpoint docs
- **Internationalization**: Multi-language support

#### Nice to Have
- **Browser Extensions**: Chrome/Firefox extensions
- **CLI Tool**: Command-line interface for power users
- **Integrations**: IDE plugins, workflow tools
- **Advanced Analytics**: ML-powered insights
- **Social Features**: Repository sharing and collaboration

## 🔄 Development Workflow

### 1. Planning Your Contribution

**Before starting work**:
- Check existing issues and PRs to avoid duplication
- Create or comment on an issue to discuss your approach
- Wait for maintainer feedback on significant changes
- Break large features into smaller, reviewable PRs

### 2. Development Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**:
   - Follow our code standards
   - Write tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add repository comparison feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**:
   - Use the PR template
   - Link related issues
   - Provide clear description
   - Include screenshots for UI changes

### 3. Pull Request Guidelines

#### PR Requirements
- [ ] **Descriptive title** following conventional commits
- [ ] **Clear description** of changes and motivation
- [ ] **Link to related issue(s)**
- [ ] **Screenshots** for UI changes
- [ ] **Tests** for new functionality
- [ ] **Documentation** updates if needed
- [ ] **No merge conflicts** with main branch

#### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] E2E tests pass (if applicable)

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project standards
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
```

## 📝 Code Standards

### TypeScript Guidelines

```typescript
// ✅ Good: Explicit types and proper naming
interface RepositorySearchParams {
  query: string;
  language?: string;
  minStars?: number;
  sortBy?: 'stars' | 'updated' | 'created';
}

async function searchRepositories(
  params: RepositorySearchParams
): Promise<Repository[]> {
  // Implementation
}

// ❌ Bad: Any types and unclear naming
function search(params: any): any {
  // Implementation
}
```

### React Component Standards

```tsx
// ✅ Good: Proper TypeScript, clear props, good structure
interface SearchResultsProps {
  repositories: Repository[];
  isLoading: boolean;
  onRepositorySelect: (repo: Repository) => void;
}

export function SearchResults({ 
  repositories, 
  isLoading, 
  onRepositorySelect 
}: SearchResultsProps) {
  if (isLoading) {
    return <SearchSkeleton />;
  }

  return (
    <div className="space-y-4">
      {repositories.map((repo) => (
        <RepositoryCard
          key={repo.id}
          repository={repo}
          onClick={() => onRepositorySelect(repo)}
        />
      ))}
    </div>
  );
}

// ❌ Bad: No types, unclear props, poor structure
export function Results({ data, loading, onClick }) {
  // Implementation
}
```

### API Route Standards

```typescript
// ✅ Good: Proper error handling, types, validation
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const searchSchema = z.object({
  q: z.string().min(1).max(100),
  page: z.number().int().min(1).default(1),
  per_page: z.number().int().min(1).max(100).default(20),
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const params = searchSchema.parse({
      q: searchParams.get('q'),
      page: Number(searchParams.get('page')) || 1,
      per_page: Number(searchParams.get('per_page')) || 20,
    });

    const results = await searchRepositories(params);
    
    return NextResponse.json({ data: results });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid parameters', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Search API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### Styling Guidelines

```tsx
// ✅ Good: Consistent Tailwind classes, semantic styling
<div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
    Repository Name
  </h3>
  <Badge variant="secondary">TypeScript</Badge>
</div>

// ❌ Bad: Mixed styling approaches, no dark mode support
<div style={{ padding: '16px' }} className="bg-white rounded">
  <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>
    Repository Name
  </h3>
</div>
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(search): add semantic search capabilities
fix(ui): resolve mobile navigation menu issue
docs(api): update endpoint documentation
refactor(analytics): optimize repository stats calculation
test(search): add unit tests for search algorithms
chore(deps): update dependencies to latest versions
```

## 🧪 Testing

### Testing Strategy

We use a comprehensive testing approach:

- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Playwright for critical user journeys
- **Visual Regression**: Chromatic for UI consistency

### Writing Tests

#### Component Tests
```typescript
// tests/components/SearchResults.test.tsx
import { render, screen } from '@testing-library/react';
import { SearchResults } from '@/components/search/SearchResults';

describe('SearchResults', () => {
  it('displays loading skeleton when loading', () => {
    render(
      <SearchResults 
        repositories={[]} 
        isLoading={true} 
        onRepositorySelect={() => {}} 
      />
    );
    
    expect(screen.getByTestId('search-skeleton')).toBeInTheDocument();
  });

  it('displays repositories when loaded', () => {
    const mockRepos = [
      { id: 1, name: 'test-repo', description: 'Test repository' }
    ];
    
    render(
      <SearchResults 
        repositories={mockRepos} 
        isLoading={false} 
        onRepositorySelect={() => {}} 
      />
    );
    
    expect(screen.getByText('test-repo')).toBeInTheDocument();
  });
});
```

#### API Tests
```typescript
// tests/api/search.test.ts
import { GET } from '@/app/api/search/route';
import { NextRequest } from 'next/server';

describe('/api/search', () => {
  it('returns search results for valid query', async () => {
    const request = new NextRequest(
      'http://localhost:3000/api/search?q=react'
    );
    
    const response = await GET(request);
    const data = await response.json();
    
    expect(response.status).toBe(200);
    expect(data.data).toBeInstanceOf(Array);
  });

  it('returns 400 for invalid parameters', async () => {
    const request = new NextRequest(
      'http://localhost:3000/api/search?q='
    );
    
    const response = await GET(request);
    
    expect(response.status).toBe(400);
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test SearchResults.test.tsx

# Run E2E tests
npm run test:e2e

# Run E2E tests in headed mode
npm run test:e2e:headed
```

## 📚 Documentation

### Code Documentation

- **Use JSDoc** for functions and complex logic
- **Add comments** for non-obvious code
- **Update README** for significant changes
- **Document APIs** with OpenAPI/Swagger specs

### Documentation Standards

```typescript
/**
 * Searches GitHub repositories using advanced filtering and ranking algorithms.
 * 
 * @param params - Search parameters including query, filters, and pagination
 * @param options - Additional options for caching and AI enhancement
 * @returns Promise resolving to paginated search results with metadata
 * 
 * @example
 * ```typescript
 * const results = await searchRepositories({
 *   query: 'machine learning',
 *   language: 'python',
 *   minStars: 100
 * });
 * ```
 */
export async function searchRepositories(
  params: SearchParams,
  options?: SearchOptions
): Promise<SearchResults> {
  // Implementation
}
```

## 🌟 Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Discord**: Real-time chat and collaboration (coming soon)
- **Email**: [help@git-search.dev](mailto:help@git-search.dev)

### Recognition

We recognize contributors in several ways:

- **Contributor List**: All contributors listed in README
- **Release Notes**: Significant contributions highlighted
- **Social Media**: Feature announcements and contributor spotlights
- **Swag**: Stickers and merchandise for regular contributors

### Mentorship

We offer mentorship for new contributors:

- **Good First Issues**: Beginner-friendly issues labeled appropriately
- **Mentor Assignment**: Experienced contributors guide newcomers
- **Code Reviews**: Detailed, educational feedback on pull requests
- **Office Hours**: Regular community calls for questions and guidance

## 📞 Contact

- **Maintainers**: [@RafiulM](https://github.com/RafiulM)
- **Email**: [contributors@git-search.dev](mailto:contributors@git-search.dev)
- **Issues**: [GitHub Issues](https://github.com/RafiulM/git-search/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RafiulM/git-search/discussions)

---

Thank you for contributing to Git Search! Your involvement helps make GitHub repository discovery better for everyone. 🚀