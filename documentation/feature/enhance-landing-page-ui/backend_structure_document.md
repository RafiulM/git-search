# Backend Structure Document

This document outlines the complete backend setup for the `git-search` application. It covers the overall architecture, database design, APIs, hosting, infrastructure, security, and maintenance practices in clear, everyday language.

## 1. Backend Architecture

The backend of `git-search` is built with a modern serverless approach, leveraging Next.js’s App Router for both page rendering and API routes. Here’s how it’s organized and why it works:

• Design Patterns & Frameworks
  - **Next.js 15 (App Router):** Handles server-side rendering (SSR), static site generation (SSG), and API routes in one framework. API routes are treated as serverless functions that scale automatically.
  - **TypeScript:** Applies type safety across the entire codebase, reducing bugs and improving developer productivity.
  - **Layered Structure:** Separates code into directories (`app`, `components`, `hooks`, `lib`, `types`) for clear concerns:
    • `app/`: Pages, layouts, and API endpoints.  
    • `components/`: Reusable UI elements.  
    • `hooks/`: Custom React hooks for data fetching.  
    • `lib/`: Utility functions and external client configurations (Supabase, Octokit).  
    • `types/`: Shared TypeScript interfaces.

• Scalability & Performance
  - **Serverless Functions:** Each API route scales independently on Vercel.  
  - **Stateless Design:** Functions don’t hold session data in memory; user sessions are managed by Clerk and Supabase.  
  - **Edge Caching & CDN:** Vercel’s global network caches static assets and serverless responses, reducing latency.
  - **Database Connection Pooling:** Supabase’s managed PostgreSQL handles connections efficiently under load.

• Maintainability
  - **Modular Code:** Clear folder structure makes it easy to locate and update features.  
  - **Environment Validation:** At startup, the app checks that critical environment variables are present.  
  - **Migrations:** Supabase SQL migration files track all database schema changes.

**Key Backend Tech Stack**
- Next.js 15 (App Router)
- TypeScript
- Clerk (authentication)
- Supabase (PostgreSQL + RLS)
- Octokit (GitHub API client)
- Vercel AI SDK
- Docker (dev container)

## 2. Database Management

The project uses Supabase’s managed PostgreSQL service as its primary data store. Here’s how data is handled:

• Database Type & System
  - **SQL Database:** PostgreSQL hosted by Supabase.
  - **Managed Service:** Automatic backups, high availability, and performance tuning provided by Supabase.

• Data Organization & Access
  - **Tables:** Stores user-specific data such as favorites, chat histories, and search logs.  
  - **Row-Level Security (RLS):** Ensures each user only sees their own data based on policies defined per table.  
  - **Migrations:** All schema changes are scripted as SQL files under the `supabase/` folder, ensuring version control.

• Data Practices
  - **Environment Isolation:** Separate development, staging, and production databases.  
  - **Backups & Point-in-Time Recovery:** Supabase automatically backs up data and allows recovery to any point in time.  
  - **Connection Pooling:** Supabase pools database connections to handle spikes in traffic without exhausting resources.

## 3. Database Schema

Below is a human-friendly overview of the main tables, followed by SQL definitions for PostgreSQL.

### Human-Readable Table Descriptions

1. **users**  
   Holds basic profile data for each authenticated user. User IDs originate from Clerk.
   - Fields: id, email, created_at

2. **favorites**  
   Tracks which GitHub repositories a user has favorited.
   - Fields: id, user_id, repo_id, repo_name, added_at

3. **featured_repositories**  
   Lists a curated set of repositories to highlight on the home page.
   - Fields: id, repo_id, repo_name, description, featured_at

4. **search_history**  
   Logs each user’s search queries for analytics and dashboard charts.
   - Fields: id, user_id, query_text, searched_at

5. **chat_history**  
   Records AI chat interactions per repository per user.
   - Fields: id, user_id, repo_id, user_message, ai_response, chatted_at

### PostgreSQL Schema Definitions

```sql
-- 1. Users
CREATE TABLE users (
  id            TEXT PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  created_at    TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. Favorites
CREATE TABLE favorites (
  id            BIGSERIAL PRIMARY KEY,
  user_id       TEXT REFERENCES users(id) ON DELETE CASCADE,
  repo_id       TEXT NOT NULL,
  repo_name     TEXT NOT NULL,
  added_at      TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 3. Featured Repositories
CREATE TABLE featured_repositories (
  id            BIGSERIAL PRIMARY KEY,
  repo_id       TEXT NOT NULL,
  repo_name     TEXT NOT NULL,
  description   TEXT,
  featured_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4. Search History
CREATE TABLE search_history (
  id            BIGSERIAL PRIMARY KEY,
  user_id       TEXT REFERENCES users(id) ON DELETE CASCADE,
  query_text    TEXT NOT NULL,
  searched_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 5. Chat History
CREATE TABLE chat_history (
  id            BIGSERIAL PRIMARY KEY,
  user_id       TEXT REFERENCES users(id) ON DELETE CASCADE,
  repo_id       TEXT NOT NULL,
  user_message  TEXT NOT NULL,
  ai_response   TEXT NOT NULL,
  chatted_at    TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 4. API Design and Endpoints

The backend exposes a set of RESTful API endpoints under `/api` to support frontend actions. All routes live in `src/app/api/`.

• GitHub Integration
  - **GET /api/github/search**  
    • Purpose: Search GitHub repositories by keywords.  
    • Process: Uses Octokit to call GitHub REST API and returns results.

  - **GET /api/github/repository/[id]**  
    • Purpose: Fetch detailed metadata for a single repository.  
    • Process: Uses Octokit and formats the response.

  - **POST /api/github/analyze**  
    • Purpose: Trigger an in-depth analysis (commit history, file tree).  
    • Process: Combines multiple GitHub API calls and returns structured data.

• Favorites Management
  - **GET /api/github/favorites**  
    • Purpose: List the user’s favorited repositories.  
    • Process: Queries the `favorites` table in Supabase.

  - **POST /api/github/favorites**  
    • Purpose: Add a repository to favorites.  
    • Payload: `{ repo_id, repo_name }`  
    • Process: Inserts a row into `favorites` with the current user.

  - **DELETE /api/github/favorites**  
    • Purpose: Remove a repository from favorites.  
    • Payload: `{ favorite_id }`  
    • Process: Deletes the corresponding row.

• AI-Powered Chat
  - **POST /api/chat**  
    • Purpose: Send user questions and get AI-driven insights on a repository.  
    • Payload: `{ repo_id, message }`  
    • Process: Forwards to Vercel AI SDK, stores conversation in `chat_history`, returns AI response.

• Dashboard & Analytics
  - **GET /api/dashboard/stats**  
    • Purpose: Retrieve user-specific metrics (search counts, favorite counts).  
    • Process: Aggregates data from `search_history`, `favorites`, and `chat_history` tables.

• Featured Repositories
  - **GET /api/repositories/featured**  
    • Purpose: Fetch the curated list of featured repositories.  
    • Process: Reads from `featured_repositories` table.

Authentication guards all endpoints dealing with user data. Clerk issues a user token that the Next.js middleware verifies before proceeding.

## 5. Hosting Solutions

• Vercel (Primary Platform)
  - Hosts the Next.js application and API routes as serverless functions.  
  - Offers automatic SSL, global CDN, and instant rollbacks.  
  - Scales on demand—no manual server management needed.

• Supabase (Database)
  - Managed PostgreSQL with built-in authentication hooks and Row-Level Security.  
  - Provides real-time capabilities if the app grows to need live updates.

• Docker Dev Container
  - Ensures every developer has a consistent local environment.  
  - Mirrors production Node.js and tooling versions.

## 6. Infrastructure Components

• Load Balancing & Routing
  - Vercel handles traffic distribution across serverless functions behind the scenes.

• Caching
  - **Vercel Edge Cache:** Caches static assets and SSR responses at edge locations.  
  - **In-Memory/Database Side:** Supabase caches query plans and uses PostgreSQL’s shared buffer.

• Content Delivery Network (CDN)
  - Vercel’s built-in CDN distributes static files and API route responses globally.

• Connection Pooling & Queuing
  - **Supabase Pooling:** Prevents database overload.  
  - **Vercel Functions:** Queue up function invocations when under heavy load.

## 7. Security Measures

• Authentication & Authorization
  - **Clerk:** Manages sign-up, sign-in, and session tokens.  
  - **Next.js Middleware:** Verifies Clerk session on protected routes and API endpoints.
  - **Row-Level Security (RLS):** Enforced at the database level so each user can only read/write their own rows.

• Data Encryption
  - **In Transit:** HTTPS everywhere (Vercel + Supabase).  
  - **At Rest:** Supabase encrypts the database storage.

• Environment Validation
  - Startup script checks for required environment variables—prevents misconfiguration in production.

• Best Practices
  - Secrets (API keys, database URLs) stored in environment variables, never in code.  
  - Rate limiting (to be added) for external GitHub API calls to avoid abuse.

## 8. Monitoring and Maintenance

• Logging & Alerts
  - **Vercel Dashboard Logs:** Real-time logs for serverless function errors and performance metrics.  
  - **Supabase Monitoring:** Tracks database performance, errors, and query statistics.

• Performance Monitoring
  - **Vercel Analytics:** Measures page load times, response times, and bandwidth usage.  
  - **Next.js Telemetry:** Optional opt-in metrics about build and runtime performance.

• Maintenance Strategies
  - **Database Migrations:** All schema changes go through versioned SQL files.  
  - **Automated Backups:** Handled by Supabase with point-in-time recovery windows.  
  - **Dependency Updates:** Regularly run dependency checks and patch critical vulnerabilities.

## 9. Conclusion and Overall Backend Summary

The `git-search` backend is a cohesive, serverless system built around Next.js API routes and a managed PostgreSQL database. It leverages modern tools—Clerk for auth, Supabase for data, Vercel for hosting—and follows best practices for scalability, security, and maintainability. Key strengths include:

- **Auto-Scaling Serverless Functions:** Ensures the API handles bursts of traffic without manual intervention.  
- **Row-Level Security:** Provides strong data isolation per user.  
- **Clear Modular Structure:** Facilitates quick onboarding and feature expansion.  
- **Global Performance:** CDN, caching, and SSR keep response times low worldwide.

This setup aligns perfectly with the project goal: offering users fast, secure, and insightful interactions with GitHub repositories, while keeping the infrastructure simple to operate and evolve.