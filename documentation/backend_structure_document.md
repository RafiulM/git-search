# Backend Structure Document

This document outlines the backend setup for the CodeGuide Starter Kit Lite v2. It explains how each piece fits together so that anyone—even without a deep technical background—can understand the architecture, databases, APIs, hosting, and infrastructure components.

## 1. Backend Architecture

**Overview:**
- The backend is built on Next.js (App Router) running serverless functions.  
- Each API route lives under `src/app/api/` and handles a single concern (for example, chat or data access).  
- Business logic is organized into small modules under `src/lib/` (e.g., Supabase client setup, environment checks, AI utilities).

**Design Patterns and Frameworks:**
- Next.js App Router for file-based routing and serverless functions.  
- Functional programming style: each route exports a handler function.  
- Dependency injection via environment variables (API keys, database URLs).  
- Middleware (`middleware.ts`) to protect routes with Clerk authentication.

**Scalability, Maintainability, and Performance:**
- Serverless functions auto-scale with demand—no manual server management.  
- Modular code organization makes it easy to add, update, or remove features.  
- Vercel’s global edge network ensures low latency for users worldwide.  
- Caching strategies (cache headers, SWR on the client) help reduce repeated data fetching.

## 2. Database Management

**Database Technology:**
- Type: SQL (relational)  
- System: Supabase (hosted PostgreSQL with real-time and authentication layers)

**How Data Is Structured and Accessed:**
- Data lives in tables inside Supabase.  
- Row Level Security (RLS) policies ensure users only see their own data.  
- Server-side code uses the Supabase client library (`@supabase/supabase-js`) for CRUD operations.  
- Client-side code can also fetch or subscribe to real-time updates when needed.

**Data Management Practices:**
- Migrations and schema changes live in the `supabase/` folder.  
- Environment variable checks prevent missing or misconfigured keys.  
- Zod schemas validate incoming data before writing to the database.

## 3. Database Schema

Below is the main schema for storing AI chat history. It uses PostgreSQL syntax.

```sql
-- Table to group messages into conversations (optional)  
CREATE TABLE conversations (  
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),  
  user_id       UUID NOT NULL,                            -- references auth.users  
  title         TEXT,                                      -- optional summary  
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()         
);

-- Table to store individual chat messages  
CREATE TABLE messages (  
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),  
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,  
  user_id       UUID NOT NULL,                               -- references auth.users  
  role          TEXT NOT NULL CHECK (role IN ('user','assistant')),  
  content       TEXT NOT NULL,                              
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()           
);

-- Example RLS policy: only allow users to see their own messages  
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;  
CREATE POLICY "Users can access their own messages" ON messages  
  FOR SELECT USING (user_id = auth.uid());
```  

If you’re not using conversations, you can omit the `conversations` table and let each message stand alone.

## 4. API Design and Endpoints

**Approach:** REST-style endpoints built as Next.js serverless functions. All endpoints live under `src/app/api/`.

**Key Endpoints:**

- **POST /api/chat**  
  Purpose: Accepts a list of prior messages and a new user prompt, forwards to the Vercel AI SDK, streams AI responses back to the client, and optionally stores the conversation in Supabase.

- **GET /api/chat/history?conversationId=...**  
  Purpose: Returns the saved message history for a given conversation (if implemented).  

- **GET /api/user/profile**  
  Purpose: Returns basic user information from Clerk (via middleware) or Supabase if extended user data is stored there.

Each endpoint:
- Checks authentication via Clerk middleware.  
- Validates input with Zod.  
- Interacts with Supabase and/or Vercel AI SDK.  
- Returns JSON with clear status codes (200 for success, 4xx for client errors).

## 5. Hosting Solutions

**Primary Hosting:** Vercel  
- Automatically builds and deploys the Next.js application on every git push.  
- Runs serverless functions for API routes—no need to manage servers.  
- Built-in CDN for static assets (images, CSS, JS).

**Development Environment:**
- Docker setup via `.devcontainer/` for consistent local development.  
- `devcontainer.json` defines Node version, extensions, and environment variable requirements.

**Benefits:**
- Zero-config auto-scaling and global edge network for fast response times.  
- Pay-as-you-go pricing—only pay for what you use.  
- Simple environment variable management in the Vercel dashboard.

## 6. Infrastructure Components

- **Load Balancer / Edge Network:** Provided by Vercel—distributes requests globally for low latency.  
- **CDN:** Vercel CDN caches static and dynamic content at edge locations.  
- **Caching Mechanisms:**  
  • Next.js `cache-control` headers  
  • Client-side SWR (stale-while-revalidate) for data fetching  
- **Database Hosting:** Supabase managed PostgreSQL with read replicas and automatic backups.  
- **Authentication Service:** Clerk’s hosted service handles sign-up, sign-in, and session management.

Together, these components ensure a smooth, fast experience for end users and an easy-to-manage infrastructure for developers.

## 7. Security Measures

- **Authentication:** Clerk protects routes and issues session tokens/cookies.  
- **Authorization:** Supabase Row Level Security (RLS) ensures users only access their own rows.  
- **Data Encryption:**  
  • TLS in transit (HTTPS everywhere)  
  • Encryption at rest on the database provider’s side  
- **Input Validation:** Zod schemas on all API inputs to prevent malicious payloads.  
- **Environment Variables:** Secrets never checked into source control; managed via Vercel dashboard or local `.env` files.  
- **HTTP Security Headers:** Configurable via Next.js custom headers (e.g., CSP, HSTS) if needed.

## 8. Monitoring and Maintenance

- **Performance Monitoring:**  
  • Vercel Analytics to track edge function performance and page load times.  
  • Supabase dashboard for database performance and query statistics.
- **Error Tracking:** Integration with Sentry or Logflare to capture unhandled exceptions in serverless routes.  
- **Logging:** Console logs in Next.js functions appear in Vercel’s Logs panel.  
- **Migrations:** Supabase migrations stored in `supabase/migrations/`. Run `supabase db push` or `supabase db migrate` as part of CI.  
- **CI/CD:**  
  • GitHub (or GitLab) integration triggers Vercel builds on each push.  
  • Optional GitHub Actions for linting, type checking, and testing before merge.

## 9. Conclusion and Overall Backend Summary

The backend of CodeGuide Starter Kit Lite v2 is built for clarity, performance, and easy scaling. By combining Next.js serverless functions, Supabase for a managed PostgreSQL database with real-time features, Clerk for secure user authentication, and the Vercel AI SDK for seamless AI chat integration, we’ve created a robust foundation. Automated hosting on Vercel and clear modular code practices make maintenance straightforward, while RLS, HTTPS, and input validation ensure user data stays safe. This backend setup aligns tightly with the project goal of delivering a modern, extensible starter kit that developers can pick up and build on immediately.