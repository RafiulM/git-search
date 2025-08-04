# Frontend Guideline Document

This document outlines the frontend setup for the **git-search** application. It covers the architecture, design principles, styling, component structure, state management, routing, performance strategies, testing, and a summary. The goal is to give anyone—technical or not—a clear picture of how the frontend is built and why it works the way it does.

## 1. Frontend Architecture

### Frameworks and Libraries
- **Next.js 15 (App Router)**: Provides page routing, server-side rendering (SSR), static site generation (SSG), and built-in API routes. Its file-based routing keeps things simple.
- **TypeScript**: Adds type safety, reducing runtime errors and improving code readability.
- **React Server Components**: Used for data fetching on the server, which shrinks the client bundle and boosts performance.
- **Tailwind CSS v4**: A utility-first CSS framework for rapid, consistent styling without writing custom CSS.
- **shadcn/ui**: A set of accessible, customizable UI components built on Radix UI and styled by Tailwind.
- **next-themes**: Manages light/dark mode toggles.
- **Clerk**: Handles user authentication, sign-up, sign-in, and session management.
- **Supabase (PostgreSQL)**: Our managed database, complete with real-time features and row-level security (RLS).
- **Vercel AI SDK**: Connects to AI models (OpenAI, Anthropic Claude) for chat-based insights.
- **Octokit**: Official GitHub API client for interacting with GitHub’s REST API.
- **Vercel**: Deployment platform with seamless Next.js support.
- **Docker (.devcontainer)**: Ensures a consistent development environment across machines.

### Scalability, Maintainability, Performance
- **Server Components & API Routes** keep heavy data work on the server, shrinking frontend bundles and speeding up load times.
- **TypeScript** and clear folder structure (`app/`, `components/`, `hooks/`, `lib/`, `types/`) help teams scale without confusion.
- **Utility-first CSS** (Tailwind) avoids large custom stylesheets and unused CSS, making style maintenance easy.
- **Managed Services** (Clerk, Supabase, Vercel) offload infrastructure concerns, letting us focus on app features.

## 2. Design Principles

### Usability
- Clear and consistent navigation (search bar always visible, simple page layouts).
- Immediate feedback for user actions (loading spinners, toast messages).

### Accessibility
- All interactive elements use semantic HTML and ARIA attributes when needed.
- Color contrasts meet WCAG AA guidelines.
- Keyboard-friendly components (dialogs, dropdowns) via `shadcn/ui`.

### Responsiveness
- Mobile-first design ensures layouts and components adapt from small to large screens.
- Tailwind breakpoints manage layout shifts smoothly.

### Application in UI
- Buttons, cards, dialogs follow a consistent look-and-feel.
- Form inputs and error states are uniform across pages.
- Loading and error states use shared components for predictability.

## 3. Styling and Theming

### Styling Approach
- **Utility-first CSS** with Tailwind (no BEM or SMACSS). We rely on Tailwind’s classes for margins, paddings, typography, and colors.
- Global styles (Tailwind base, components, utilities) are imported in `globals.css`.

### Theming
- **next-themes** handles theme context (`light` and `dark`). We wrap the root layout in a `ThemeProvider`.
- Theme toggle is a shared component (`ThemeToggle`) that switches classes on `<html>`.

### Visual Style
- **Overall Feel**: Modern flat design with subtle glassmorphism touches on select cards (slightly blurred translucent backgrounds) to highlight AI chat and featured repositories.

### Color Palette
- Primary: #3B82F6  (blue-500)
- Secondary: #6366F1  (indigo-500)
- Accent: #F59E0B   (amber-500)
- Background Light: #F9FAFB  (gray-50)
- Background Dark: #111827  (gray-900)
- Surface Light: #FFFFFF  (white)
- Surface Dark: #1F2937  (gray-800)
- Text Light: #111827  (gray-900)
- Text Dark: #F3F4F6  (gray-100)

### Fonts
- **Primary Font**: Inter, sans-serif
- **Fallbacks**: system-ui, -apple-system, BlinkMacSystemFont

## 4. Component Structure

### Organization
- `src/components/`: Reusable React components.
  - `ui/`: shadcn/ui primitives (buttons, inputs, dialogs).
  - App-specific components (`Chat`, `ThemeToggle`, `RepositoryCard`).
- `src/app/`: Next.js app router (pages, layouts, API routes).
- `src/hooks/`: Custom hooks (`useRepositorySearch`, `useDashboardStats`).
- `src/lib/`: Client configs and utilities (Supabase client, `env-check`).
- `src/types/`: TypeScript interfaces and types.

### Benefits of Component-Based Architecture
- **Reusability**: Build once, use everywhere (e.g., `Button`, `Card`).
- **Isolation**: Changes in one component rarely affect others.
- **Clarity**: Easy to locate and update specific UI parts.

## 5. State Management

### Approaches and Libraries
- **React Query** (via a `QueryProvider`): Manages server state (data fetching, caching, background updates).
- **React Context**: Shares theme and auth state (through Clerk’s provider and `next-themes`).
- **Local State**: `useState` and `useReducer` for component-specific states (form inputs, modal open/close).

### Data Flow
1. Component calls a custom hook (e.g., `useRepositorySearch`).
2. Hook uses React Query to fetch from an internal API route.
3. React Query caches and shares data across components.
4. UI components read query data and show loading/error states automatically.

## 6. Routing and Navigation

### Routing
- **Next.js App Router**: File-based routing (`src/app/page.tsx`, `src/app/search/page.tsx`, etc.).
- Dynamic segments (`[slug]`) for repository detail pages.

### Protected Routes
- **Middleware** (`middleware.ts`): Checks Clerk session and redirects unauthorized users away from `/dashboard` or `/favorites`.

### Navigation Structure
- Top-level menu or header with links to Home, Search, Dashboard, Favorites.
- `next/link` ensures client-side transitions.
- Breadcrumbs on detail pages for easy back navigation.

## 7. Performance Optimization

- **Server Components** reduce client JS bundle size.
- **SSR/SSG**: Pre-renders key pages for instant load.
- **Code Splitting**: Next.js automatically splits by route.
- **Lazy Loading**: Dynamic `import()` for heavy components (e.g., AI chat panel).
- **Image Optimization**: Next.js `Image` component auto-optimizes images.
- **Tailwind Purge**: Removes unused CSS in production builds.
- **Caching**: React Query caches API responses. Consider adding Redis or edge caching for GitHub data in the future.

## 8. Testing and Quality Assurance

### Testing Strategies
- **Unit Tests**: Jest or Vitest + React Testing Library for components, hooks, and utilities.
- **Integration Tests**: API route tests to simulate GitHub and Supabase interactions (using mocks).
- **End-to-End (E2E) Tests**: Playwright or Cypress to cover core user flows (search, login, favorite).

### Tools and Configuration
- **ESLint** with a shared config (`eslint.config.mjs`) for linting rules.
- **Prettier** (`.prettierrc`) for consistent formatting.
- **TypeScript** (`tsconfig.json`) to catch type errors early.
- **Git Hooks** (via Husky or simple npm scripts) to run linters and tests before commits.

## 9. Conclusion and Overall Frontend Summary

The **git-search** frontend is built with a modern, scalable stack centered on Next.js and TypeScript. We prioritize:
- **Performance**: Server components, SSR/SSG, code splitting.
- **Maintainability**: Clear folder structure, TypeScript, utility-first styling.
- **Accessibility**: Semantic HTML, ARIA attributes, accessible UI components.
- **User Experience**: Responsive design, theming, fast feedback.

By following these guidelines—consistent design principles, component-based architecture, robust state management, and thorough testing—we ensure the frontend remains reliable, easy to extend, and aligned with user needs as the application grows.
