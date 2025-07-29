# Contributing to Git Search

🎉 Thank you for your interest in contributing to Git Search! We welcome contributions from developers of all experience levels.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Reporting Issues](#reporting-issues)
- [Community](#community)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and constructive in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, make sure you have:

- Node.js 18+ installed
- Git installed and configured
- A GitHub account
- Basic knowledge of TypeScript, React, and Next.js

### Development Setup

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/git-search.git
   cd git-search
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/RafiulM/git-search.git
   ```

3. **Install dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Fill in your API keys and environment variables
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

6. **Verify the setup**
   - Open [http://localhost:3000](http://localhost:3000)
   - Ensure the application loads correctly

## 🛠️ How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes** - Fix existing issues
- ✨ **New features** - Add new functionality
- 📝 **Documentation** - Improve docs, READMEs, code comments
- 🎨 **UI/UX improvements** - Enhance user interface and experience
- ⚡ **Performance optimizations** - Make the app faster
- 🧪 **Tests** - Add or improve test coverage
- 🔧 **Refactoring** - Improve code quality and structure

### Finding Work

1. **Check existing issues** - Look for issues labeled `good first issue` or `help wanted`
2. **Create new issues** - If you find bugs or have feature ideas
3. **Join discussions** - Participate in GitHub Discussions

## 📥 Pull Request Process

### Before You Start

1. **Create an issue** first to discuss major changes
2. **Check existing PRs** to avoid duplication
3. **Assign yourself** to the issue you're working on

### Step-by-Step Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes**
   - Follow our coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   npm run lint          # Check linting
   npm run build         # Ensure it builds
   npm run test          # Run tests (if available)
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add search filtering by language"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template completely
   - Link to related issues
   - Add screenshots for UI changes

### PR Requirements

- ✅ All tests pass
- ✅ Code follows our style guidelines
- ✅ Documentation updated (if applicable)
- ✅ No merge conflicts
- ✅ Descriptive commit messages
- ✅ PR template filled out

## 🎨 Coding Standards

### TypeScript Guidelines

- Use TypeScript for all new code
- Define proper types and interfaces
- Avoid `any` type when possible
- Use strict mode settings

### Code Style

- Use Prettier for formatting
- Follow ESLint rules
- Use meaningful variable and function names
- Write self-documenting code
- Add comments for complex logic

### File Organization

```
src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── search/       # Search-specific components
│   └── common/       # Shared components
├── lib/              # Utility functions
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
└── utils/            # Helper functions
```

### Component Guidelines

- Use functional components with hooks
- Extract custom hooks for reusable logic
- Keep components small and focused
- Use proper prop types
- Handle loading and error states

### API Guidelines

- Use proper HTTP status codes
- Implement error handling
- Add input validation
- Document API endpoints
- Use consistent response formats

## 🧪 Testing Guidelines

### Testing Framework

We use Jest and React Testing Library for testing.

### Writing Tests

- Write tests for new features
- Include edge cases
- Test user interactions
- Mock external dependencies
- Aim for meaningful test coverage

### Running Tests

```bash
npm run test          # Run all tests
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Run tests with coverage
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Clear title** - Briefly describe the issue
- **Steps to reproduce** - Detailed reproduction steps
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Environment details** - OS, browser, Node.js version
- **Screenshots** - If applicable
- **Additional context** - Any other relevant information

### Feature Requests

For feature requests, please include:

- **Problem description** - What problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought of
- **Additional context** - Why is this important?

### Issue Labels

We use labels to categorize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high/medium/low` - Priority level

## 🤝 Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General discussions and questions
- **Pull Requests** - Code review and collaboration

### Getting Help

If you need help:

1. Check existing documentation
2. Search GitHub Issues for similar questions
3. Create a new issue with the `question` label
4. Join GitHub Discussions

### Recognition

Contributors are recognized in:

- **README.md** - Major contributors listed
- **Release notes** - Contributions highlighted
- **GitHub contributions** - Automatic recognition

## 📝 Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/issue-number` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance tasks

Examples:
```
feat(search): add language filter to repository search
fix(ui): resolve dark mode toggle issue on mobile
docs(readme): update installation instructions
```

### Release Process

1. Features merged to `main` branch
2. Regular releases with semantic versioning
3. Release notes generated automatically
4. Contributors acknowledged in releases

## 🎯 Roadmap

Check our [GitHub Projects](https://github.com/RafiulM/git-search/projects) to see:

- Current sprint goals
- Upcoming features
- Long-term roadmap
- Issue priorities

## 📚 Resources

### Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Project Resources

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

## 🙏 Thank You

Thank you for contributing to Git Search! Your contributions help make this tool better for developers worldwide.

**Happy coding! 🚀✨**