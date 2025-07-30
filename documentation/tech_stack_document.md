# Tech Stack Document

This document explains the technology choices behind the CodeGuide Starter Kit Lite v2 in everyday language. It shows what each technology does and why it was chosen to build a modern, secure, and scalable Next.js starter kit.

## Frontend Technologies

We chose a set of tools and libraries to create a fast, flexible, and beautiful user interface:

- **Next.js 15 (App Router)**
  - A React framework that handles page routing, server-side rendering, and image optimizations out of the box.
  - Enhances performance and SEO by pre-rendering pages on the server.
- **TypeScript (strict mode)**
  - A typed version of JavaScript that catches errors early and improves code readability.
  - Helps teams maintain large codebases with confidence.
- **Tailwind CSS v4**
  - A utility-first CSS framework that lets you style elements by combining small, reusable classes.
  - Speeds up development and keeps CSS consistent and maintainable.
- **shadcn/ui (New York style)**
  - A headless, unstyled component library that provides building blocks (buttons, cards, dialogs, etc.) without enforcing a design.
  - Allows designers and developers to apply their own Tailwind-based styling on top.
- **next-themes**
  - A theme management library that enables light/dark mode switching with minimal setup.
  - Works seamlessly with Tailwind CSS’s dark mode utilities.
- **React Context**
  - A simple state-management solution built into React for passing data (like user info or theme) through the component tree without prop drilling.

Together, these tools ensure the front end is:

- **Fast**: Server-side rendering, optimized bundling, and Tailwind’s atomic classes minimize CSS bloat.
- **Flexible**: Headless components + utility CSS mean you can adapt the look and feel to any brand.
- **Developer-Friendly**: TypeScript and clear folder structure help developers onboard quickly.

## Backend Technologies

On the server side, we use well-integrated services and frameworks to handle authentication, data storage, and AI-powered features:

- **Next.js API Routes**
  - Built into Next.js for creating serverless endpoints (e.g., `/api/chat/route.ts`).
  - Handles requests without managing a separate server.
- **Clerk** (Authentication)
  - Provides pre-built UI components and middleware for sign-up, sign-in, and user session management.
  - Middleware protects sensitive routes, ensuring only authenticated users can access them.
- **Supabase** (Database)
  - A hosted PostgreSQL database with built-in real-time subscriptions and authentication hooks.
  - Row Level Security (RLS) ensures each user only sees or modifies their own data.
- **Vercel AI SDK**
  - Simplifies integration with AI models from OpenAI and Anthropic Claude.
  - Powers the real-time streaming chat interface by handling streaming responses.
- **Additional Libraries**
  - **zod**: Validates data coming in and out (e.g., API request bodies).
  - **react-hook-form**: Manages complex forms (e.g., sign-up forms) with minimal code.
  - **date-fns**: Parses and formats dates in a lightweight way.
  - **svix**: Manages webhooks for any external event handling you may add.

These backend pieces work together to provide:

- **Secure authentication** via Clerk.
- **Reliable data storage** and access control via Supabase + RLS.
- **AI-driven features** without manual model setup.

## Infrastructure and Deployment

To ensure the project is easy to deploy, maintain, and scale, we rely on proven infrastructure and workflows:

- **Version Control: Git**
  - Tracks changes, enables collaboration, and integrates with CI/CD pipelines.
- **Development Environment: Docker (.devcontainer)**
  - Defines a reproducible environment for developers using Visual Studio Code’s Remote Containers.
- **Hosting & Deployment: Vercel**
  - Automatically builds and deploys Next.js apps on every push.
  - Built-in support for environment variables and serverless functions.
- **CI/CD Pipelines**
  - You can plug in GitHub Actions or Vercel’s own pipelines to run tests and linting on every commit.

These choices make the project:

- **Reliable**: Automated builds and tests prevent bad code from reaching production.
- **Scalable**: Vercel auto-scales serverless functions and static assets.
- **Portable**: Docker ensures that all developers share the same local setup.

## Third-Party Integrations

We integrate several external services that add powerful features without building them from scratch:

- **Clerk**: User authentication and session management.
- **Supabase**: Hosted PostgreSQL database with real-time features and row-level security.
- **OpenAI & Anthropic Claude** (via Vercel AI SDK): AI models for chat and content generation.
- **svix**: Reliable webhook management in case you connect to external systems.
- **Embla Carousel** (`embla-carousel-react`): Touch-friendly carousels for a better mobile experience.
- **Lucide React**: A set of crisp, open-source icons.
- **Sonner**: Lightweight toast notifications for user feedback.
- **Tailwind Merge**: Safely combines multiple Tailwind class strings.

Each integration:

- **Speeds up development** by offloading complex logic.
- **Improves functionality** with battle-tested services (e.g., secure auth, real-time DB updates).

## Security and Performance Considerations

We’ve baked in security and speed optimizations to ensure a smooth and safe user experience:

- **Authentication & Access Control**
  - Clerk protects routes and handles secure session cookies.
  - Supabase RLS policies restrict data access at the database level.
- **Environment Variable Checks**
  - `lib/env.ts` or similar utilities verify that all required keys and URLs are set before the app starts.
- **Data Validation**
  - `zod` schemas validate incoming request data to prevent injection attacks.
- **Performance Optimizations**
  - Server-side rendering (SSR) for critical pages reduces load times and improves SEO.
  - Real-time streaming of AI responses avoids holding up the UI.
  - Tailwind CSS’s tree-shaking removes unused styles from the final build.

Together, these measures protect user data and deliver snappy interactions.

## Conclusion and Overall Tech Stack Summary

We combined industry-leading frameworks, cloud services, and libraries to meet the project goals:

- **Modern UX**: Next.js, Tailwind CSS, shadcn/ui, and next-themes deliver a fast, customizable interface.
- **Secure & Scalable Backend**: Clerk, Supabase, and Vercel AI SDK provide authentication, data storage, and AI features without heavy setup.
- **Smooth Developer Experience**: TypeScript, Docker, and clear folder structures help new contributors get up to speed quickly.
- **Reliability**: Automated CI/CD, environment checks, and best-practice security policies ensure a rock-solid foundation.

Unique aspects that set this starter kit apart:

- **Headless component library** (shadcn/ui) for full design control.
- **Built-in AI integration** supporting multiple models.
- **Row-level security** baked into your database from day one.

This Tech Stack Document should give non-technical and technical stakeholders alike a clear picture of why each tool was chosen and how they work together to deliver a robust Next.js starter kit.