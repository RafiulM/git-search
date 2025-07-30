# Project Requirements Document (PRD)

## 1. Project Overview

The **CodeGuide Starter Kit Lite v2** is a ready-to-go Next.js starter template aimed at giving developers a kick-start when building modern web applications. It combines authentication, database, AI, UI components, and theming into one opinionated, well-structured codebase. Instead of wiring up Clerk, Supabase, Tailwind, shadcn/ui, and Vercel AI SDK from scratch, you clone this repo, set your environment variables, and you’re up and running.

We’re building this starter kit to eliminate repetitive setup tasks and enforce best practices out of the box: secure user sign-in/sign-up, row-level security, real-time AI chat, dark-mode toggle, and a cohesive UI. **Success** looks like:  
1. New users can spin up a full-stack app in under 10 minutes.  
2. All core integrations work together smoothly.  
3. The codebase stays clean, documented, and easy to extend.

---

## 2. In-Scope vs. Out-of-Scope

### In-Scope (v1.0)
- User authentication with Clerk (sign-up, sign-in, middleware-protected routes).  
- Database integration via Supabase (CRUD + Row Level Security).  
- AI chat interface using Vercel AI SDK (OpenAI & Anthropic Claude), with real-time streaming.  
- UI components from shadcn/ui (New York style) and theme support (light/dark).  
- TailwindCSS v4 for styling, CSS custom properties for theming.  
- Basic environment variable validation and `.env.example`.  
- Clear README & setup guides (Clerk + Supabase + AI).  

### Out-of-Scope (for later phases)
- Payment processing (Stripe, PayPal).  
- Mobile apps or React Native support.  
- Complex data visualization beyond simple charts.  
- Internationalization (i18n).  
- Multi-tenant administration panel.  
- Automated end-to-end testing suites (Cypress, Playwright).  

---

## 3. User Flow

When a user lands on the homepage, they see a brief introduction, a sign-in/sign-up prompt, and a link to the AI chat demo. Unauthenticated visitors can browse public pages and see the theme toggle, but attempts to access the chat or profile pages redirect them to Clerk’s hosted sign-in page. Once signed in, the user is redirected back to the dashboard, now fully unlocked.

On the dashboard, users see the real-time AI chat widget, powered by Vercel AI SDK. They type messages and watch AI responses stream in. A left-corner user button opens a menu to view profile info or sign out. The theme toggle switches between light and dark instantly, thanks to `next-themes`. Behind the scenes, every chat, user profile update, or demo data CRUD operation is stored in Supabase with proper Row Level Security.

---

## 4. Core Features

- **Authentication**  
  - Clerk integration for sign-up, sign-in, sign-out.  
  - Middleware protects `/dashboard`, `/profile`.  
  - Clerk UI components: `SignInButton`, `SignedIn`, `SignedOut`, `UserButton`.  

- **Database Integration**  
  - Supabase client for server & client data fetching.  
  - Full CRUD support on demo tables.  
  - Row Level Security policies based on Clerk user ID.  

- **AI Integration**  
  - Vercel AI SDK configured for OpenAI & Anthropic Claude.  
  - Streaming chat API at `/api/chat/route.ts`.  
  - Clerk-protected AI endpoints.  

- **UI Components & Layout**  
  - Headless, accessible components from shadcn/ui.  
  - Prebuilt elements: buttons, cards, dialogs, inputs, navigation.  

- **Styling & Theming**  
  - TailwindCSS v4 with utility classes.  
  - CSS custom properties for colors & spacing.  
  - Dark mode via `next-themes`.  

- **Environment Setup**  
  - `.env.example` with variables for Clerk, Supabase, OpenAI, Claude.  
  - Runtime checks to fail fast if variables are missing.  

---

## 5. Tech Stack & Tools

- **Frontend Framework:** Next.js 15 (App Router)  
- **Language:** TypeScript (strict mode)  
- **Styling:** TailwindCSS v4 + CSS variables  
- **UI Library:** shadcn/ui (New York style)  
- **Authentication:** Clerk SDK + Middleware  
- **Database:** Supabase (PostgreSQL + RLS)  
- **AI Integration:** Vercel AI SDK  
  - OpenAI models  
  - Anthropic Claude models  
- **State Management:** React Context (minimal)  
- **Theme Management:** next-themes  
- **Dev Environment:**  
  - Docker + `.devcontainer` for VS Code  
  - ESLint, Prettier config included  
- **Version Control:** Git (GitHub recommended)  
- **Additional Libraries:** clsx, cmdk, date-fns, embla-carousel-react, input-otp, lucide-react, react-hook-form, react-resizable-panels, recharts, sonner, svix, tailwind-merge, vaul, zod  

---

## 6. Non-Functional Requirements

- **Performance**:  
  - Initial page load < 1.5s on 3G.  
  - AI streaming response latency < 300ms per token.  

- **Security**:  
  - All protected endpoints require Clerk JWT.  
  - Supabase RLS policies to enforce per-user data access.  
  - Environment secrets never exposed to client.  

- **Maintainability**:  
  - Well-structured file layout matching Next.js conventions.  
  - Inline JSDoc/TSDoc comments.  
  - Clear separation of concerns (UI vs. data vs. utils).  

- **Usability**:  
  - Zero-configuration setup after `.env` is populated.  
  - Accessible UI components (ARIA, keyboard nav).  

- **Scalability**:  
  - Modular feature folders for easy extension.  
  - Stateless API routes for horizontal scaling.  

- **Documentation**:  
  - Step-by-step README + supplementary markdown (CLAUDE.md, SUPABASE_CLERK_SETUP.md).  

- **Testing**:  
  - Unit tests for critical utilities (e.g., env checks, Supabase client).  
  - Placeholder integration tests recommended.  

---

## 7. Constraints & Assumptions

- **Third-Party Services**  
  - Clerk must support the chosen domain for OAuth redirect.  
  - Supabase project must be provisioned with correct RLS settings.  
  - OpenAI & Anthropic Claude API keys must be valid and unthrottled.  

- **Developer Environment**  
  - Node.js v18+ installed.  
  - Docker available if using `.devcontainer`.  

- **Assumptions**  
  - Users have basic Git and VS Code experience.  
  - No custom branding is required in v1.0.  
  - AI usage quotas are sufficient for demo purposes.  

---

## 8. Known Issues & Potential Pitfalls

- **API Rate Limits**  
  - OpenAI/Claude quotas may throttle heavy usage.  
  - Mitigation: implement exponential back-off and caching.  

- **RLS Misconfiguration**  
  - Missing or overly permissive policies can leak data.  
  - Mitigation: include sample SQL for strict per-user RLS rules.  

- **Environment Variable Typos**  
  - Typos in `.env` keys lead to confusing runtime errors.  
  - Mitigation: runtime guard functions that validate and log missing vars.  

- **Version Mismatch**  
  - Next.js, Tailwind, and shadcn/ui updates might break compatibility.  
  - Mitigation: lock dependencies in `package.json` and note upgrade path.  

- **CORS & Cookies**  
  - Clerk and Supabase require correct cookie settings on production domains.  
  - Mitigation: document cookie domains in setup guide.  

---

*End of PRD*