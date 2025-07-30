"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  ArrowLeft, 
  Star, 
  GitFork, 
  Eye, 
  Calendar, 
  FileText, 
  BarChart3,
  ExternalLink,
  Code,
  Zap,
  PieChart,
  Activity,
  TrendingUp,
  Database,
  Clock,
  Package
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { ThemeToggle } from '@/components/theme-toggle';
import MermaidDiagram from '@/components/mermaid-diagram';
import Link from 'next/link';

// Enhanced dummy repository data with comprehensive documentation
const repositoryData = {
  "facebook-react": {
    name: "facebook/react",
    description: "The library for web and native user interfaces",
    language: "JavaScript",
    stars: 227000,
    forks: 46000,
    watchers: 6800,
    lastUpdated: "2024-01-15",
    githubUrl: "https://github.com/facebook/react",
    license: "MIT",
    defaultBranch: "main",
    openIssues: 1200,
    size: 15600, // KB
    createdAt: "2013-05-24",
    topics: ["javascript", "react", "frontend", "library", "components", "jsx", "virtual-dom"],
    stats: {
      linesOfCode: 125000,
      characters: 4200000,
      files: 1250,
      directories: 180,
      storageSize: "15.2 MB",
      tokenEstimates: {
        gpt4: 1200000,
        claude: 933000,
        gemini: 1050000
      },
      complexity: 7.2,
      maintainability: 82.5,
      languageBreakdown: {
        "JavaScript": 85.2,
        "TypeScript": 8.7,
        "HTML": 3.1,
        "CSS": 1.8,
        "Other": 1.2
      },
      fileTypeBreakdown: {
        ".js": 450,
        ".ts": 320,
        ".json": 180,
        ".md": 95,
        ".html": 85,
        ".css": 75,
        "other": 45
      },
      largestFiles: [
        { path: "packages/react-dom/src/client/ReactDOMRoot.js", size: "45.2 KB" },
        { path: "packages/react-reconciler/src/ReactFiberWorkLoop.js", size: "38.7 KB" },
        { path: "packages/react/src/ReactHooks.js", size: "32.1 KB" },
        { path: "packages/scheduler/src/Scheduler.js", size: "28.9 KB" },
        { path: "packages/react-dom/src/events/DOMPluginEventSystem.js", size: "25.4 KB" }
      ]
    },
    documentation: {
      summary: `# React - The Library for Web and Native User Interfaces

## Overview
React is a JavaScript library for building user interfaces, particularly web applications. It allows developers to create large web applications that can change data, without reloading the page.

## Key Features
- **Component-Based**: Build encapsulated components that manage their own state
- **Declarative**: React makes it painless to create interactive UIs
- **Learn Once, Write Anywhere**: Develop new features without rewriting existing code
- **Virtual DOM**: Efficient rendering through virtual representation of UI
- **Hooks**: Use state and other React features without writing a class

## Architecture
React follows a unidirectional data flow architecture where data flows down from parent to child components through props, and events bubble up through callback functions.

## Community & Ecosystem
With over 227,000 stars on GitHub and a massive ecosystem of tools, libraries, and resources, React has one of the largest and most active communities in the frontend development world.`,

      requirements: `# React Project Requirements Document

## Technical Requirements

### System Requirements
- **Node.js**: Version 16.0 or higher
- **npm**: Version 8.0 or higher (or yarn equivalent)
- **Browser Support**: Modern browsers (ES6+ support)

### Development Environment
- Modern code editor with JavaScript/JSX support
- Git for version control
- Terminal/Command line access

## Functional Requirements

### Core Features
- Component rendering and state management
- Event handling and user interactions
- Lifecycle methods and hooks support
- Props and context API functionality
- Server-side rendering capabilities

### Performance Requirements
- Fast initial render (< 100ms for simple components)
- Efficient re-rendering through virtual DOM
- Memory efficient component lifecycle
- Bundle size optimization

## Development Standards
- Follow React coding conventions
- Use TypeScript for type safety (recommended)
- Implement proper error boundaries
- Write comprehensive tests`,

      techStack: `# React Technology Stack Analysis

## Core Technologies
- **JavaScript/TypeScript**: Primary programming language
- **JSX**: JavaScript XML syntax extension
- **Babel**: JavaScript compiler for modern syntax
- **Webpack**: Module bundler for production builds

## Development Tools
- **ESLint**: Code linting and style enforcement
- **Prettier**: Code formatting
- **Jest**: Testing framework
- **React Testing Library**: Component testing utilities

## Build System
- **Create React App**: Default scaffolding tool
- **Vite**: Modern build tool alternative
- **Next.js**: Full-stack React framework
- **Gatsby**: Static site generator

## State Management
- **Built-in State**: useState and useReducer hooks
- **Context API**: Global state management
- **Redux**: Predictable state container
- **Zustand**: Lightweight state management

## Styling Solutions
- **CSS Modules**: Scoped CSS
- **Styled Components**: CSS-in-JS solution
- **Tailwind CSS**: Utility-first CSS framework
- **Emotion**: Performant CSS-in-JS library`,

      frontendGuidelines: `# React Frontend Development Guidelines

## Component Architecture

### Component Design Principles
- **Single Responsibility**: Each component should have one clear purpose
- **Composition over Inheritance**: Use composition to build complex UIs
- **Props Interface**: Define clear and consistent props interfaces
- **Reusability**: Design components to be reusable across the application

### File Organization
\`\`\`
src/
├── components/          # Reusable UI components
│   ├── common/         # Shared components
│   └── ui/             # Basic UI elements
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── context/            # React context providers
├── utils/              # Utility functions
└── types/              # TypeScript type definitions
\`\`\`

## Coding Standards

### Component Structure
\`\`\`jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const MyComponent = ({ prop1, prop2, ...props }) => {
  const [state, setState] = useState(initialValue);
  
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  const handleEvent = (event) => {
    // Event handler logic
  };
  
  return (
    <div {...props}>
      {/* Component JSX */}
    </div>
  );
};

MyComponent.propTypes = {
  prop1: PropTypes.string.required,
  prop2: PropTypes.number
};

export default MyComponent;
\`\`\`

### Hooks Guidelines
- Use built-in hooks appropriately (useState, useEffect, useContext)
- Create custom hooks for reusable logic
- Follow hooks rules (only call at top level)
- Optimize dependencies to prevent unnecessary re-renders

## Performance Best Practices
- Use React.memo for expensive components
- Implement proper key props for lists
- Lazy load components with React.Suspense
- Optimize bundle size with code splitting`,

      backendStructure: `# React Backend Integration Architecture

## API Integration Patterns

### HTTP Client Setup
\`\`\`javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;
\`\`\`

### Data Fetching Patterns
\`\`\`javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export const useApi = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get(url, options);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
};
\`\`\`

## State Management Architecture

### Context API Structure
\`\`\`javascript
// context/AppContext.js
import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
\`\`\`

## Backend Communication
- RESTful API integration
- GraphQL support via Apollo Client
- WebSocket connections for real-time features
- Authentication token management
- Error handling and retry logic`,

      appFlow: `# React Application Flow Documentation

## Component Lifecycle Flow

### Mounting Phase
1. **Constructor/Initial State**: Component initialization
2. **Render**: Initial JSX rendering
3. **ComponentDidMount/useEffect**: Side effects after mount
4. **State Updates**: User interactions trigger state changes

### Update Phase
1. **Props/State Change**: New props received or state updated
2. **Re-render**: Component re-renders with new data
3. **Effect Cleanup**: Previous effects cleaned up
4. **New Effects**: New effects run based on dependencies

### Unmounting Phase
1. **Effect Cleanup**: All effects are cleaned up
2. **Component Removal**: Component removed from DOM

## User Interaction Flow

### Event Handling Pipeline
1. **User Action**: Click, input, scroll, etc.
2. **Event Handler**: Function called with event object
3. **State Update**: setState or dispatch called
4. **Re-render Trigger**: Component queued for re-render
5. **Virtual DOM Diff**: Changes calculated
6. **DOM Update**: Minimal changes applied to real DOM

## Data Flow Architecture

### Unidirectional Data Flow
\`\`\`
Parent Component
    ↓ (props)
Child Component
    ↓ (props)
Grandchild Component
    ↑ (callbacks)
Event Handlers
    ↑ (state updates)
Parent State
\`\`\`

### Context API Flow
\`\`\`
Context Provider
    ↓ (value)
Consumer Components
    ↓ (actions)
Context Reducer
    ↓ (new state)
All Subscribed Components Re-render
\`\`\`

## Application Initialization
1. **Index.js**: App entry point
2. **App Component**: Root component mount
3. **Router Setup**: Route configuration
4. **Provider Wrapping**: Context providers initialized
5. **Initial Route**: Default route rendered
6. **Data Fetching**: Initial API calls made`,

      flowchart: `# React Application Architecture Flowchart

This diagram shows the high-level architecture and data flow of a typical React application.

## Key Components
- **User Interface**: Browser-based React components
- **State Management**: Context API or Redux store
- **Backend API**: REST or GraphQL endpoints
- **External Services**: Third-party integrations

## Data Flow
The application follows React's unidirectional data flow pattern where data flows down through props and events bubble up through callbacks.`
    },
    mermaidDiagram: `graph TB
    A[User Interface] --> B[React Components]
    B --> C{State Management}
    C -->|Local State| D[useState/useReducer]
    C -->|Global State| E[Context API]
    C -->|Complex State| F[Redux Store]
    
    B --> G[Event Handlers]
    G --> H[API Calls]
    H --> I[Backend Services]
    I --> J[(Database)]
    
    H --> K[External APIs]
    K --> L[Third-party Services]
    
    B --> M[Component Tree]
    M --> N[Parent Components]
    N --> O[Child Components]
    O --> P[Props Flow Down]
    P --> Q[Events Flow Up]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style I fill:#fff3e0`
  },
  // Add similar data structure for other repositories...
  "microsoft-vscode": {
    name: "microsoft/vscode",
    description: "Visual Studio Code - Open Source Build",
    language: "TypeScript",
    stars: 163000,
    forks: 28000,
    watchers: 3500,
    lastUpdated: "2024-01-14",
    githubUrl: "https://github.com/microsoft/vscode",
    license: "MIT",
    defaultBranch: "main",
    openIssues: 5200,
    size: 149300,
    createdAt: "2015-09-03",
    topics: ["typescript", "editor", "electron", "ide", "code-editor"],
    stats: {
      linesOfCode: 890000,
      characters: 28500000,
      files: 8500,
      directories: 1200,
      storageSize: "145.8 MB",
      tokenEstimates: {
        gpt4: 8140000,
        claude: 6333000,
        gemini: 7125000
      },
      complexity: 8.9,
      maintainability: 75.3,
      languageBreakdown: {
        "TypeScript": 78.4,
        "JavaScript": 12.1,
        "CSS": 4.2,
        "HTML": 2.8,
        "Other": 2.5
      },
      fileTypeBreakdown: {
        ".ts": 3200,
        ".js": 1800,
        ".json": 980,
        ".css": 650,
        ".html": 420,
        ".md": 280,
        "other": 1170
      },
      largestFiles: [
        { path: "src/vs/workbench/workbench.desktop.main.ts", size: "125.7 KB" },
        { path: "src/vs/editor/contrib/suggest/suggestController.ts", size: "98.3 KB" },
        { path: "src/vs/workbench/services/extensions/electron-browser/extensionService.ts", size: "87.2 KB" }
      ]
    },
    documentation: {
      summary: "Visual Studio Code is a lightweight but powerful source code editor with rich editing features, integrated debugging, and extensive extensibility through a robust marketplace ecosystem.",
      requirements: "Node.js 16+, Electron framework, TypeScript compiler, and various build tools for cross-platform desktop application development.",
      techStack: "Built with Electron, TypeScript, Monaco Editor, and a comprehensive plugin architecture supporting hundreds of programming languages and frameworks.",
      frontendGuidelines: "Electron-based desktop application with web technologies, using TypeScript for type safety and modular architecture for extensibility.",
      backendStructure: "Language servers, extension host processes, and integrated terminal support with cross-platform compatibility.",
      appFlow: "Multi-process architecture with main process, renderer processes, and extension host processes for security and performance isolation."
    },
    mermaidDiagram: `graph TB
    A[VS Code Main Process] --> B[Renderer Process]
    A --> C[Extension Host Process]
    B --> D[Monaco Editor]
    B --> E[Workbench UI]
    C --> F[Language Servers]
    C --> G[Extensions]
    F --> H[IntelliSense]
    F --> I[Diagnostics]
    G --> J[Custom Commands]
    G --> K[UI Contributions]`
  }
};

export default function RepositoryPage() {
  const params = useParams();
  const repo = params.repo as string;
  const [repository, setRepository] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call delay
    setTimeout(() => {
      const repoData = repositoryData[repo as keyof typeof repositoryData];
      setRepository(repoData || null);
      setLoading(false);
    }, 500);
  }, [repo]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div className="flex items-center gap-4">
                <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              </div>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="h-12 w-96 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-8" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              ))}
            </div>
            <div className="space-y-6">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!repository) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-xl font-semibold mb-2">Repository not found</h3>
              <p className="text-muted-foreground mb-4">
                The repository you&apos;re looking for doesn&apos;t exist in our database.
              </p>
              <Link href="/">
                <Button>Back to Home</Button>
              </Link>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Back
                </Button>
              </Link>
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Git Search
              </Link>
            </div>
            
            <div className="flex items-center gap-4">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Repository Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">{repository.name}</h1>
              <p className="text-muted-foreground text-lg">
                {repository.description}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <a href={repository.githubUrl} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm">
                  <ExternalLink className="w-4 h-4 mr-1" />
                  View on GitHub
                </Button>
              </a>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex flex-wrap items-center gap-6 text-sm mb-4">
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="font-medium">{formatNumber(repository.stars)}</span>
              <span className="text-muted-foreground">stars</span>
            </div>
            <div className="flex items-center gap-1">
              <GitFork className="w-4 h-4 text-blue-500" />
              <span className="font-medium">{formatNumber(repository.forks)}</span>
              <span className="text-muted-foreground">forks</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4 text-green-500" />
              <span className="font-medium">{formatNumber(repository.watchers)}</span>
              <span className="text-muted-foreground">watching</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span className="text-muted-foreground">Updated {formatDate(repository.lastUpdated)}</span>
            </div>
          </div>

          {/* Topics */}
          {repository.topics && repository.topics.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {repository.topics.map((topic: string) => (
                <Badge key={topic} variant="secondary">
                  {topic}
                </Badge>
              ))}
            </div>
          )}
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="files">Files</TabsTrigger>
            <TabsTrigger value="documentation">Documentation</TabsTrigger>
            <TabsTrigger value="flowchart">Flowchart</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Stats */}
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      AI-Focused Statistics
                    </CardTitle>
                    <CardDescription>
                      Comprehensive code analysis for AI development workflows
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(repository.stats.linesOfCode)}
                        </div>
                        <div className="text-sm text-muted-foreground">Lines of Code</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {repository.stats.files}
                        </div>
                        <div className="text-sm text-muted-foreground">Files</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {repository.stats.storageSize}
                        </div>
                        <div className="text-sm text-muted-foreground">Storage Size</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {formatNumber(repository.stats.characters)}
                        </div>
                        <div className="text-sm text-muted-foreground">Characters</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* AI Token Estimates */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      AI Model Token Estimates
                    </CardTitle>
                    <CardDescription>
                      Estimated input tokens for different AI models
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-xl font-semibold">GPT-4</div>
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(repository.stats.tokenEstimates.gpt4)}
                        </div>
                        <div className="text-sm text-muted-foreground">estimated tokens</div>
                      </div>
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-xl font-semibold">Claude 3</div>
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(repository.stats.tokenEstimates.claude)}
                        </div>
                        <div className="text-sm text-muted-foreground">estimated tokens</div>
                      </div>
                      <div className="text-center p-4 border rounded-lg">
                        <div className="text-xl font-semibold">Gemini</div>
                        <div className="text-2xl font-bold text-purple-600">
                          {formatNumber(repository.stats.tokenEstimates.gemini)}
                        </div>
                        <div className="text-sm text-muted-foreground">estimated tokens</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Repository Info */}
                <Card>
                  <CardHeader>
                    <CardTitle>Repository Info</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Primary Language</span>
                      <span className="font-medium">{repository.language}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">License</span>
                      <span className="font-medium">{repository.license}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Size</span>
                      <span className="font-medium">{formatBytes(repository.size * 1024)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Default Branch</span>
                      <span className="font-medium">{repository.defaultBranch}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Open Issues</span>
                      <span className="font-medium">{repository.openIssues}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Created</span>
                      <span className="font-medium">{formatDate(repository.createdAt)}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Language Breakdown */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5" />
                      Languages
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(repository.stats.languageBreakdown)
                      .sort(([,a], [,b]) => (b as number) - (a as number))
                      .map(([language, percentage]) => (
                        <div key={language}>
                          <div className="flex justify-between text-sm mb-1">
                            <span>{language}</span>
                            <span>{(percentage as number).toFixed(1)}%</span>
                          </div>
                          <Progress value={percentage as number} className="h-2" />
                        </div>
                      ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="statistics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Code Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-2xl font-bold">{formatNumber(repository.stats.linesOfCode)}</div>
                      <div className="text-sm text-muted-foreground">Total Lines</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{formatNumber(repository.stats.characters)}</div>
                      <div className="text-sm text-muted-foreground">Characters</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{repository.stats.files}</div>
                      <div className="text-sm text-muted-foreground">Files</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{repository.stats.directories}</div>
                      <div className="text-sm text-muted-foreground">Directories</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quality Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Complexity Score</span>
                      <span className="font-medium">{repository.stats.complexity.toFixed(1)}/10</span>
                    </div>
                    <Progress value={repository.stats.complexity * 10} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Maintainability Index</span>
                      <span className="font-medium">{repository.stats.maintainability.toFixed(1)}/100</span>
                    </div>
                    <Progress value={repository.stats.maintainability} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>File Type Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(repository.stats.fileTypeBreakdown).map(([type, count]) => (
                      <div key={type} className="text-center p-3 border rounded">
                        <div className="text-lg font-bold">{count as number}</div>
                        <div className="text-sm text-muted-foreground">{type}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="files" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Largest Files</CardTitle>
                <CardDescription>Files that contribute most to the repository size</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {repository.stats.largestFiles.map((file: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-2">
                        <Code className="w-4 h-4" />
                        <span className="font-mono text-sm">{file.path}</span>
                      </div>
                      <span className="text-sm text-muted-foreground">{file.size}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documentation" className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Project Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.summary}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Requirements Document</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.requirements}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Technology Stack</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.techStack}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Frontend Guidelines</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.frontendGuidelines}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Backend Structure</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.backendStructure}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Application Flow</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg text-sm">
                      {repository.documentation.appFlow}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="flowchart" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Architecture Flowchart</CardTitle>
                <CardDescription>
                  {repository.documentation.flowchart}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border rounded-lg p-4 bg-white dark:bg-muted">
                  <MermaidDiagram chart={repository.mermaidDiagram} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}