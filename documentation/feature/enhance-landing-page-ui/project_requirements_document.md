# Project Requirements Document (PRD)

## 1. Project Overview

**git-search** is a full-stack web application built with Next.js that lets developers and curious users search, explore, and analyze GitHub repositories in a single, user-friendly interface. Beyond simple keyword lookups, it offers in-depth repository metrics (commit history, file structure, contributor stats) and an AI-powered chat assistant that can explain code patterns, suggest improvements, and answer natural-language questions about any repo. Users can sign up to personalize their experience, save favorite repositories, and monitor their activity on a custom dashboard.

The project exists to bridge the gap between raw GitHub data and meaningful insights. Instead of jumping between pages on GitHub and separate analytics tools, users can stay in one place to discover projects, dive deep into their health and trends, and get AI-driven explanations. Key success criteria include fast search response times, accurate repository analysis, reliable AI chat interactions, secure and seamless authentication, and an intuitive UI with both light and dark themes.

## 2. In-Scope vs. Out-of-Scope

**In-Scope (Version 1):**
- GitHub repository search by keyword, topic, or criteria.
- Detailed repository analysis (commit history, file tree, contributor stats, code metrics).
- AI-powered chat interface for natural-language insights (using OpenAI and Anthropic Claude via Vercel AI SDK).
- User authentication (sign-up/sign-in) and session management via Clerk.
- Favorites management: add/remove bookmarks stored in Supabase with Row-Level Security.
- Personalized dashboard showing search history, favorites count, recent AI chats, and basic usage stats.
- Light and dark theme toggling using next-themes.
- Serverless API routes for search, analysis, AI chat, favorites, and dashboard stats.

**Out-of-Scope (Phase 1):**
- Direct pull request creation or issue management on GitHub.
- In-browser code editing or live previews of repository code.
- Enterprise or on-premises deployment support.
- Mobile-specific native apps (iOS/Android) or PWA offline support.
- Advanced analytics (e.g., graph visualizations, time-series comparisons) beyond basic stats.
- Third-party integrations beyond GitHub and AI models (e.g., Jira, Slack).

## 3. User Flow

A new visitor lands on the homepage, which prominently features a search bar. They type keywords and hit “Search.” Behind the scenes, the frontend calls the `/api/github/search` endpoint, which uses Octokit to fetch matching repositories. Results appear in a paginated list with repo name, description, star count, and a “View Details” button. The user clicks a repo, and the app navigates to `/repository/[slug]`, where detailed stats (commit history, file structure, contributor breakdown) are displayed server-side for performance.

If the visitor wants to save a repo, they click “Sign Up,” complete the Clerk-powered authentication flow, and return to the repo page. Logged-in users can favorite repositories, which triggers a POST to `/api/github/favorites`. Their favorites list is visible under `/favorites`, and their dashboard at `/dashboard` shows saved repos, search usage patterns, and recent AI chats. On any repo page, users can open the chat widget, type questions (“How many contributors were active last month?”), and receive AI-generated insights, powered by the Vercel AI SDK.

## 4. Core Features

- **Authentication**: Clerk handles user sign-up, sign-in, and session management. Protects `/dashboard` and `/favorites` with middleware.
- **Search Module**: Frontend component and `/api/github/search` route that queries GitHub via Octokit and returns paginated results.
- **Repository Analysis**: Detailed view powered by `/api/github/repository/[id]` and `/api/github/analyze` routes fetching commit history, file tree, and statistics.
- **AI Chat Interface**: Reusable React component that sends user prompts to Vercel AI SDK, selectable between OpenAI and Anthropic Claude models, and displays responses conversationally.
- **Favorites Management**: Protected API routes to add/remove favorites in Supabase, leveraging RLS to isolate each user’s data.
- **Dashboard & Analytics**: Aggregates user activity via `/api/dashboard/stats` (search count, favorites count, recent chats) and displays charts or summary cards.
- **Theming**: Global light/dark mode toggle using next-themes, persisted in `localStorage`.
- **API Layer**: Next.js serverless routes under `src/app/api` for all back-end interactions (GitHub, Supabase, AI).

## 5. Tech Stack & Tools

- Frontend: Next.js 15 (App Router), React 18 Server and Client Components, TypeScript.
- Styling & UI: Tailwind CSS v4, shadcn/ui (Radix UI + Tailwind), next-themes.
- Authentication: Clerk.js.
- Database: Supabase (PostgreSQL) with Row-Level Security for favorites.
- AI Integration: Vercel AI SDK connecting to OpenAI GPT-4 and Anthropic Claude.
- GitHub API: Octokit REST client.
- Deployment: Vercel serverless platform.
- Development Environment: Docker devcontainer, VS Code with ESLint & Prettier, optional Cursor or Windsurf plugins for AI-powered coding assistance.

## 6. Non-Functional Requirements

- **Performance:** Page load under 2 seconds on a 3G connection. Search results returned in under 1 second. AI chat responses in under 1.5 seconds.
- **Scalability:** Support up to 5,000 daily users without manual scaling; leverage Vercel auto-scaling and Supabase managed infrastructure.
- **Security:** HTTPS everywhere; Clerk session tokens with HTTP-only cookies; Supabase RLS enforced; OWASP Top 10 mitigations in API routes.
- **Compliance:** GDPR-compatible data storage; clear privacy policy; opt-out for analytics.
- **Usability & Accessibility:** WCAG 2.1 AA standards; keyboard navigable; ARIA attributes on custom components; color contrast checks.

## 7. Constraints & Assumptions

- **GitHub API Rate Limits:** 5,000 requests/hour per OAuth app. Assume caching or rate-limiting logic is needed.
- **AI Model Availability:** Dependent on OpenAI/Anthropic quotas and response times. Assume keys and quotas are provisioned.
- **Environment Variables:** Validated at startup via `lib/env-check.ts`. Must include GitHub token, Clerk credentials, Supabase URL/key, AI API keys.
- **Next.js App Router:** Requires Node.js 18+ and Vercel platform features.
- **User Base:** Primarily English-speaking developers/researchers.

## 8. Known Issues & Potential Pitfalls

- **API Rate Limiting:** Exceeding GitHub limits may lead to 403 errors. Mitigation: implement server-side caching (in-memory or Redis) for repeated queries.
- **AI Model Cost & Latency:** Heavy chat usage can incur high costs and slower responses. Mitigation: add usage quotas per user and fallback static suggestions when AI delays.
- **Data Consistency:** Concurrent favorites operations could conflict. Mitigation: use Supabase transactions and optimistic UI updates.
- **SSR vs. CSR Data Fetching:** Over-fetching in Server Components may slow page builds. Mitigation: split heavy data calls to client components or use incremental static regeneration (ISR).
- **Environment Drift:** Developers may miss environment variable updates. Mitigation: include comprehensive `.env.example` and pre-launch environment checks.

---

This PRD provides a clear, unambiguous reference for the AI model and subsequent technical documents, ensuring every feature, flow, and constraint is fully specified for implementation.