import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase';
import { Octokit } from '@octokit/rest';

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

async function generateDocumentation(owner: string, repo: string, docType: string) {
  try {
    // Fetch repository information
    const { data: repoData } = await octokit.rest.repos.get({
      owner,
      repo,
    });

    // Fetch README if available
    let readmeContent = '';
    try {
      const { data: readme } = await octokit.rest.repos.getReadme({
        owner,
        repo,
      });
      if ('content' in readme) {
        readmeContent = Buffer.from(readme.content, 'base64').toString('utf-8');
      }
    } catch {
      console.log('No README found');
    }

    // Fetch package.json or similar config files for tech stack analysis
    let packageJsonContent = '';
    let techStack: string[] = [];
    try {
      const { data: packageJson } = await octokit.rest.repos.getContent({
        owner,
        repo,
        path: 'package.json',
      });
      if ('content' in packageJson) {
        packageJsonContent = Buffer.from(packageJson.content, 'base64').toString('utf-8');
        const pkgData = JSON.parse(packageJsonContent);
        
        // Extract tech stack from dependencies
        const dependencies = { ...pkgData.dependencies, ...pkgData.devDependencies };
        techStack = Object.keys(dependencies).slice(0, 20); // Top 20 dependencies
      }
    } catch {
      console.log('No package.json found');
    }

    // Generate documentation based on type
    let title = '';
    let content = '';
    let mermaidDiagram = '';

    switch (docType) {
      case 'summary':
        title = 'Repository Summary';
        content = generateSummary({
          full_name: repoData.full_name,
          description: repoData.description || undefined,
          language: repoData.language || undefined,
          stargazers_count: repoData.stargazers_count,
          forks_count: repoData.forks_count,
          open_issues_count: repoData.open_issues_count,
          license: repoData.license ? { name: repoData.license.name } : undefined,
          created_at: repoData.created_at,
          updated_at: repoData.updated_at,
          topics: repoData.topics || undefined,
          has_wiki: repoData.has_wiki,
          has_pages: repoData.has_pages,
          has_issues: repoData.has_issues,
          has_projects: repoData.has_projects,
          archived: repoData.archived,
          fork: repoData.fork,
        }, readmeContent);
        break;
      
      case 'tech_stack':
        title = 'Technology Stack';
        content = generateTechStackDoc({
          language: repoData.language || undefined,
        }, techStack);
        break;
      
      case 'requirements':
        title = 'Project Requirements';
        content = generateRequirementsDoc({
          full_name: repoData.full_name,
          description: repoData.description || undefined,
          language: repoData.language || undefined,
          license: repoData.license ? { name: repoData.license.name } : undefined,
        }, readmeContent);
        break;
      
      case 'frontend_guidelines':
        title = 'Frontend Development Guidelines';
        content = generateFrontendGuidelines({
          full_name: repoData.full_name,
          language: repoData.language || undefined,
        }, techStack);
        break;
      
      case 'backend_structure':
        title = 'Backend Architecture';
        content = generateBackendStructure({
          full_name: repoData.full_name,
          language: repoData.language || undefined,
        }, techStack);
        break;
      
      case 'app_flow':
        title = 'Application Flow';
        content = generateAppFlow({
          full_name: repoData.full_name,
          description: repoData.description || undefined,
        });
        break;
      
      case 'flowchart':
        title = 'Architecture Flowchart';
        content = generateFlowchartDoc(repoData, techStack);
        mermaidDiagram = generateMermaidFlowchart(repoData, techStack);
        break;
      
      default:
        throw new Error('Invalid documentation type');
    }

    return { title, content, mermaidDiagram };
  } catch (error) {
    console.error('Documentation generation error:', error);
    throw error;
  }
}

function generateSummary(repoData: {
  full_name: string;
  description?: string;
  language?: string;
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
  license?: { name: string };
  created_at: string;
  updated_at: string;
  topics?: string[];
  has_wiki: boolean;
  has_pages: boolean;
  has_issues: boolean;
  has_projects: boolean;
  archived: boolean;
  fork: boolean;
}, readmeContent: string): string {
  return `# ${repoData.full_name}

## Overview
${repoData.description || 'No description available'}

## Repository Details
- **Primary Language**: ${repoData.language || 'Not specified'}
- **Stars**: ${repoData.stargazers_count}
- **Forks**: ${repoData.forks_count}
- **Open Issues**: ${repoData.open_issues_count}
- **License**: ${repoData.license?.name || 'No license'}
- **Created**: ${new Date(repoData.created_at).toLocaleDateString()}
- **Last Updated**: ${new Date(repoData.updated_at).toLocaleDateString()}

## Topics
${repoData.topics?.join(', ') || 'No topics specified'}

## Features
${repoData.has_wiki ? '✅ Wiki available' : '❌ No wiki'}
${repoData.has_pages ? '✅ GitHub Pages enabled' : '❌ No GitHub Pages'}
${repoData.has_issues ? '✅ Issues enabled' : '❌ Issues disabled'}
${repoData.has_projects ? '✅ Projects enabled' : '❌ No projects'}

## README Content Summary
${readmeContent ? 'README file is available with detailed information.' : 'No README file found.'}

## Development Status
${repoData.archived ? '🗄️ **ARCHIVED** - This repository is no longer actively maintained' : '🚀 **ACTIVE** - This repository is actively maintained'}
${repoData.fork ? '🍴 This is a fork of another repository' : '🌟 This is an original repository'}
`;
}

function generateTechStackDoc(repoData: { language?: string }, techStack: string[]): string {
  const primaryLang = repoData.language || 'Unknown';
  
  let content = `# Technology Stack Analysis

## Primary Language
**${primaryLang}**

## Core Dependencies
`;

  if (techStack.length > 0) {
    content += techStack.map(dep => `- ${dep}`).join('\n');
  } else {
    content += 'No dependency information available';
  }

  content += `

## Framework Detection
`;

  // Detect frameworks based on dependencies
  const frameworks = [];
  if (techStack.includes('react') || techStack.includes('next')) {
    frameworks.push('React/Next.js Frontend');
  }
  if (techStack.includes('vue') || techStack.includes('nuxt')) {
    frameworks.push('Vue.js Frontend');
  }
  if (techStack.includes('angular')) {
    frameworks.push('Angular Frontend');
  }
  if (techStack.includes('express') || techStack.includes('fastify')) {
    frameworks.push('Node.js Backend');
  }
  if (techStack.includes('django') || techStack.includes('flask')) {
    frameworks.push('Python Web Framework');
  }

  if (frameworks.length > 0) {
    content += frameworks.map(fw => `- ${fw}`).join('\n');
  } else {
    content += 'No specific frameworks detected';
  }

  content += `

## Development Tools
`;

  const devTools = [];
  if (techStack.includes('typescript')) devTools.push('TypeScript');
  if (techStack.includes('eslint')) devTools.push('ESLint');
  if (techStack.includes('prettier')) devTools.push('Prettier');
  if (techStack.includes('jest') || techStack.includes('vitest')) devTools.push('Testing Framework');
  if (techStack.includes('webpack') || techStack.includes('vite')) devTools.push('Build Tool');

  if (devTools.length > 0) {
    content += devTools.map(tool => `- ${tool}`).join('\n');
  } else {
    content += 'No specific development tools detected';
  }

  return content;
}

function generateRequirementsDoc(repoData: { full_name: string; description?: string; language?: string; license?: { name: string } }, readmeContent: string): string {
  return `# Project Requirements Document

## Project Overview
**Repository**: ${repoData.full_name}
**Description**: ${repoData.description || 'No description provided'}

## Functional Requirements
Based on the repository analysis, this project likely includes:

### Core Features
- Primary functionality related to ${repoData.language || 'software development'}
- User interface components (if frontend project)
- Data processing capabilities (if backend project)
- Integration with external services (if applicable)

### User Stories
- As a user, I want to access the main functionality
- As a developer, I want to understand the codebase structure
- As a maintainer, I want to ensure code quality and documentation

## Technical Requirements

### System Requirements
- **Primary Language**: ${repoData.language || 'Not specified'}
- **Platform Compatibility**: Based on language choice
- **Browser Support**: Modern browsers (if web application)

### Performance Requirements
- Response time should be optimized for user experience
- Code should follow best practices for the chosen technology stack
- Scalability considerations based on project scope

## Quality Requirements
- Code should be well-documented
- Unit tests should be implemented where applicable
- Code style should be consistent throughout the project

## Constraints
- Open source license: ${repoData.license?.name || 'No license specified'}
- GitHub repository constraints
- Language and framework limitations

## Installation Requirements
${readmeContent.includes('install') || readmeContent.includes('setup') ? 
  'Installation instructions are available in the README file.' : 
  'Installation requirements need to be documented.'}

## Maintenance Requirements
- Regular updates to dependencies
- Security vulnerability monitoring
- Documentation updates as features evolve
`;
}

function generateFrontendGuidelines(repoData: { full_name: string; language?: string }, techStack: string[]): string {
  const isReact = techStack.includes('react');
  const isVue = techStack.includes('vue');
  const isAngular = techStack.includes('angular');
  const hasTypeScript = techStack.includes('typescript');

  return `# Frontend Development Guidelines

## Project Overview
**Repository**: ${repoData.full_name}
**Primary Language**: ${repoData.language}

## Framework Guidelines
${isReact ? `
### React Development
- Use functional components with hooks
- Implement proper state management
- Follow React best practices for component composition
- Use TypeScript for type safety${hasTypeScript ? ' (already configured)' : ' (recommended)'}
` : ''}

${isVue ? `
### Vue.js Development
- Use Vue 3 Composition API
- Implement proper reactive state management
- Follow Vue style guide
- Use TypeScript for better developer experience${hasTypeScript ? ' (already configured)' : ' (recommended)'}
` : ''}

${isAngular ? `
### Angular Development
- Follow Angular style guide
- Use Angular CLI for code generation
- Implement proper dependency injection
- Use TypeScript${hasTypeScript ? ' (already configured)' : ' (required)'}
` : ''}

## Code Style Guidelines

### File Organization
- Organize files by feature or functionality
- Use consistent naming conventions
- Separate concerns (components, services, utilities)

### Component Guidelines
- Keep components small and focused
- Use props/inputs for data flow
- Implement proper error handling
- Add meaningful comments for complex logic

### Styling Guidelines
- Use CSS modules or styled-components for component isolation
- Follow responsive design principles
- Maintain consistent design system
- Use CSS preprocessors if beneficial

## Testing Guidelines
- Write unit tests for components
- Implement integration tests for user flows
- Use testing utilities appropriate for the framework
- Aim for meaningful test coverage

## Performance Guidelines
- Optimize bundle size
- Implement code splitting where appropriate
- Use lazy loading for routes
- Optimize images and assets

## Accessibility Guidelines
- Follow WCAG guidelines
- Use semantic HTML elements
- Implement proper ARIA attributes
- Test with screen readers

## Development Workflow
- Use version control effectively
- Follow consistent commit message format
- Implement code review process
- Use linting and formatting tools${techStack.includes('eslint') ? ' (ESLint configured)' : ''}${techStack.includes('prettier') ? ' (Prettier configured)' : ''}
`;
}

function generateBackendStructure(repoData: { full_name: string; language?: string }, techStack: string[]): string {
  const isNode = techStack.includes('express') || techStack.includes('fastify') || repoData.language === 'JavaScript';
  const isPython = repoData.language === 'Python' || techStack.includes('django') || techStack.includes('flask');

  return `# Backend Architecture Documentation

## Project Overview
**Repository**: ${repoData.full_name}
**Primary Language**: ${repoData.language}

## Architecture Overview
This backend project follows modern software architecture principles with clear separation of concerns.

${isNode ? `
## Node.js Architecture
### Directory Structure
\`\`\`
src/
├── controllers/     # Request handlers
├── services/        # Business logic
├── models/          # Data models
├── routes/          # API route definitions
├── middleware/      # Custom middleware
├── config/          # Configuration files
├── utils/           # Utility functions
└── tests/           # Test files
\`\`\`

### Framework: ${techStack.includes('express') ? 'Express.js' : techStack.includes('fastify') ? 'Fastify' : 'Node.js'}
- RESTful API design
- Middleware-based request processing
- Async/await for asynchronous operations
` : ''}

${isPython ? `
## Python Architecture
### Framework: ${techStack.includes('django') ? 'Django' : techStack.includes('flask') ? 'Flask' : 'Python'}
### Directory Structure
\`\`\`
app/
├── models/          # Data models
├── views/           # Request handlers
├── services/        # Business logic
├── serializers/     # Data serialization
├── urls.py          # URL routing
├── settings.py      # Configuration
└── tests/           # Test files
\`\`\`
` : ''}

## API Design Principles
- RESTful endpoint design
- Consistent response formats
- Proper HTTP status codes
- Comprehensive error handling
- Input validation and sanitization

## Data Layer
- Database abstraction layer
- ORM/ODM for data operations
- Migration management
- Connection pooling

## Security Considerations
- Authentication and authorization
- Input validation
- SQL injection prevention
- CORS configuration
- Rate limiting

## Error Handling
- Centralized error handling
- Meaningful error messages
- Proper logging
- Graceful degradation

## Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Database testing with test fixtures
- Performance testing for critical paths

## Deployment Considerations
- Environment configuration
- Database migrations
- Health check endpoints
- Monitoring and logging
- Containerization (if applicable)

## Performance Optimization
- Database query optimization
- Caching strategies
- Connection pooling
- Async processing for heavy operations
`;
}

function generateAppFlow(repoData: { full_name: string; description?: string }): string {
  return `# Application Flow Documentation

## Project Overview
**Repository**: ${repoData.full_name}
**Description**: ${repoData.description || 'No description provided'}

## User Journey
Based on the repository structure and purpose, the typical user flow includes:

### 1. Entry Point
- Users access the application through the main interface
- Initial loading and authentication (if required)
- Landing page or dashboard presentation

### 2. Core Functionality
- Main feature interaction
- Data input and processing
- Real-time updates (if applicable)

### 3. Data Processing
- Input validation and sanitization
- Business logic execution
- Database operations
- External API integrations (if any)

### 4. Response and Feedback
- Results presentation to user
- Error handling and user feedback
- Success confirmations

## Technical Flow

### Frontend Flow
1. **Initialization**
   - Application bootstrap
   - Route setup
   - State initialization

2. **User Interaction**
   - Event handling
   - State updates
   - API calls

3. **Data Management**
   - Local state management
   - Cache management
   - Persistence layer

### Backend Flow (if applicable)
1. **Request Reception**
   - Route matching
   - Middleware processing
   - Input validation

2. **Business Logic**
   - Service layer execution
   - Data processing
   - External integrations

3. **Response Generation**
   - Data formatting
   - Error handling
   - Response transmission

## Error Handling Flow
- Input validation errors
- Network connectivity issues
- Server-side errors
- User-friendly error messages
- Fallback mechanisms

## Security Flow
- Authentication verification
- Authorization checks
- Input sanitization
- Output encoding
- Session management

## Performance Considerations
- Lazy loading strategies
- Caching mechanisms
- Database optimization
- Network request optimization
- Resource management

## Monitoring and Logging
- User interaction tracking
- Error logging
- Performance metrics
- System health monitoring
`;
}

function generateFlowchartDoc(repoData: { full_name: string }, techStack: string[]): string {
  return `# Architecture Flowchart

## System Overview
This flowchart represents the high-level architecture of ${repoData.full_name}.

## Components
- **Frontend**: User interface layer
- **Backend**: Server-side logic${techStack.length > 0 ? ` (${techStack.slice(0, 3).join(', ')})` : ''}
- **Database**: Data persistence layer
- **External Services**: Third-party integrations

## Data Flow
1. User initiates action in frontend
2. Frontend sends request to backend
3. Backend processes request and queries database
4. Backend returns response to frontend
5. Frontend updates user interface

## Key Interactions
- User authentication and authorization
- CRUD operations on data
- Real-time updates (if applicable)
- Error handling and recovery

The mermaid diagram below shows the detailed flow between components.
`;
}

function generateMermaidFlowchart(repoData: { full_name: string }, techStack: string[]): string {
  const isFullStack = techStack.some(dep => 
    ['react', 'vue', 'angular', 'next'].includes(dep)
  ) && techStack.some(dep => 
    ['express', 'fastify', 'django', 'flask'].includes(dep)
  );

  if (isFullStack) {
    return `graph TB
    A[User] --> B[Frontend UI]
    B --> C{Authentication}
    C -->|Authenticated| D[Main Application]
    C -->|Not Authenticated| E[Login Page]
    E --> C
    D --> F[API Requests]
    F --> G[Backend Server]
    G --> H[Authentication Middleware]
    H --> I[Route Handlers]
    I --> J[Business Logic]
    J --> K[Database]
    K --> J
    J --> I
    I --> G
    G --> F
    F --> D
    D --> B`;
  } else {
    return `graph TB
    A[User] --> B[Application Entry]
    B --> C[Initialization]
    C --> D[Core Functionality]
    D --> E[Data Processing]
    E --> F[Results/Output]
    F --> G[User Feedback]
    G --> D
    
    subgraph "Error Handling"
    H[Input Validation]
    I[Error Processing]
    J[User Notification]
    end
    
    D --> H
    H --> I
    I --> J
    J --> D`;
  }
}

export async function POST(request: NextRequest) {
  try {
    const { repository_id, doc_type } = await request.json();

    if (!repository_id || !doc_type) {
      return NextResponse.json(
        { error: 'Repository ID and document type are required' },
        { status: 400 }
      );
    }

    const supabase = await createSupabaseServerClient();

    // Get repository information
    const { data: repository } = await supabase
      .from('repositories')
      .select('*')
      .eq('id', repository_id)
      .single();

    if (!repository) {
      return NextResponse.json(
        { error: 'Repository not found' },
        { status: 404 }
      );
    }

    const [owner, repo] = repository.name.split('/');
    const { title, content, mermaidDiagram } = await generateDocumentation(owner, repo, doc_type);

    // Save documentation to database
    const { data: documentation } = await supabase
      .from('documents')
      .insert({
        repository_id,
        document_type: doc_type,
        title,
        content,
        generated_by: 'system',
        is_current: true,
        version: 1,
      })
      .select()
      .single();

    return NextResponse.json({
      success: true,
      documentation,
    });

  } catch (error) {
    console.error('Documentation generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate documentation' },
      { status: 500 }
    );
  }
}