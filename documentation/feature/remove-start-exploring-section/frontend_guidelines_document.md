# Frontend Guideline Document

## 1. Frontend Architecture

### 1.1 Overview
Our frontend is built as a modern Next.js application (v15) using the App Router. We use TypeScript for type safety and clarity. Styling comes from Tailwind CSS v4, and we layer on headless components from shadcn/ui (New York style). Authentication is handled by Clerk, data lives in Supabase (with Row Level Security), and AI features are powered by the Vercel AI SDK (supporting OpenAI and Anthropic Claude). We manage themes using next-themes and state with React Context. A handful of utility libraries (clsx, date-fns, zod, and more) support specialized features.

### 1.2 Why This Architecture Works
- **Scalability**: Next.js’s file-based routing and API routes let us grow pages and serverless endpoints without complex wiring. Supabase handles scaling the database, and Vercel AI SDK abstracts AI model interactions.  
- **Maintainability**: TypeScript plus a clear folder structure (`app/`, `components/`, `lib/`, etc.) keeps code predictable. shadcn/ui components are headless and composable, so we avoid one-off styles.  
- **Performance**: We use server-side rendering (SSR) where needed, static generation for public pages, and dynamic imports for large components. Tailwind’s tree-shaking strips unused CSS. Next.js image and script optimizations ensure fast loads.

## 2. Design Principles

### 2.1 Usability
- We keep interfaces clean and consistent: buttons look and behave the same everywhere.  
- Form flows (like sign-up and AI chat) guide users with clear labels, inline validation, and helpful error messages.

### 2.2 Accessibility (A11y)
- All interactive elements (buttons, links, inputs) have proper ARIA roles and labels.  
- We maintain color contrast ratios above WCAG AA standards.  
- Keyboard navigation is fully supported, and focus states are visible.

### 2.3 Responsiveness
- We use Tailwind’s responsive utilities (`sm:`, `md:`, `lg:`) to adapt layouts from mobile to desktop.  
- Components flex and wrap naturally (using Flexbox and CSS Grid) so content never overflows.

### 2.4 Consistency
- A shared design system (shadcn/ui + theme tokens) ensures spacing, typography, and color usage align across the app.

## 3. Styling and Theming

### 3.1 Styling Approach
- We follow a utility-first approach with Tailwind CSS v4.  
- Custom properties (CSS variables) define primary colors, spacing, and fonts.  
- For component-level logic (like conditional classes), we use the `clsx` library.

### 3.2 CSS Methodology
- We don’t adopt BEM or SMACSS explicitly; instead, Tailwind’s atomic classes keep styles modular.  
- global styles (e.g., resets) live in `globals.css`, and theme variables in `:root` selectors.

### 3.3 Theming
- next-themes manages a light and dark theme.  
- We define theme tokens (`--color-bg`, `--color-text`, etc.) and update them at runtime.  
- The `ThemeToggle` component switches themes and persists the choice in `localStorage`.

### 3.4 Visual Style
- Overall style: Modern flat design with subtle glassmorphism accents (semi-transparent panels with soft shadows).  
- UI components from shadcn/ui ensure a minimal, elegant look.

### 3.5 Color Palette
| Token          | Light Hex | Dark Hex  | Usage            |
| -------------- | --------- | --------- | ---------------- |
| --color-primary| #1E3A8A   | #93C5FD   | Buttons, links   |
| --color-secondary| #64748B | #475569   | Cards, backgrounds|
| --color-accent | #9333EA   | #A78BFA   | Highlights       |
| --color-bg     | #FFFFFF   | #0F172A   | Page background  |
| --color-text   | #111827   | #F1F5F9   | Main text        |
| --color-danger | #DC2626   | #FCA5A5   | Errors, alerts   |

### 3.6 Typography
- Primary font: Inter (system fallback: -apple-system, BlinkMacSystemFont, sans-serif)  
- Headings and body share the same font, with size scale defined in Tailwind config (e.g., `text-xl`, `text-2xl`).

## 4. Component Structure

### 4.1 Organization
- `src/components/ui/`: shadcn/ui wrapper components and shared UI bits.  
- `src/components/`: app-specific components (Chat, ThemeToggle, SetupGuide, etc.).  
- `src/app/`: page layouts, route files, and API routes.

### 4.2 Reusability
- Each component has its own folder with a single TSX file and optional styles or tests.  
- Props are fully typed; side effects (hooks) are separated into `src/lib/` when shared.

### 4.3 Benefits of Component-Based Architecture
- Changes in one component don’t ripple unpredictably.  
- Composable pieces speed up new feature development.  
- Easier to test and document in isolation.

## 5. State Management

### 5.1 Local and Shared State
- Local UI state lives in component state (`useState`, `useReducer`).  
- Shared data (user session, theme) lives in React Context providers under `src/app/layout.tsx`.

### 5.2 Patterns and Libraries
- We rely on React Context + hooks for simple cross-component state.  
- For forms, we use `react-hook-form` and schema validation with `zod`.  
- For API data, we fetch directly via Supabase client or AI SDK; caching is minimal by design but can be extended with React Query if needed.

## 6. Routing and Navigation

### 6.1 Next.js App Router
- File-based routing under `src/app/`. Each folder with `page.tsx` becomes a route.  
- Nested layouts (`layout.tsx`) share providers and UI structure (header, footer).

### 6.2 Protected Routes
- Clerk’s middleware (`middleware.ts`) guards specific paths (`/dashboard`, `/profile`).  
- Unauthenticated users are automatically redirected to Clerk’s sign-in page.

### 6.3 Navigation Components
- We use shadcn/ui Nav components and `next/link` for internal navigation.  
- Mobile menus use `cmdk` or custom popovers for a smooth experience.

## 7. Performance Optimization

### 7.1 Code Splitting & Lazy Loading
- Dynamic imports (`next/dynamic`) for heavy or rarely used components (e.g., chat transcript viewer).  
- Inline critical CSS via Tailwind’s JIT engine.

### 7.2 Asset Optimization
- Next.js Image component handles image resizing and lazy loading.  
- SVG icons (via lucide-react) are inlined for faster paint.

### 7.3 Caching and Server-Side Rendering
- Public pages use static generation (`export const revalidate`).  
- Private pages use SSR with Clerk session checks.
- HTTP caching headers set in Next.js config where appropriate.

## 8. Testing and Quality Assurance

### 8.1 Unit Testing
- Jest + React Testing Library for components and hooks.  
- We mock Supabase client and Clerk session in tests.

### 8.2 Integration Testing
- React Testing Library to simulate user flows (sign-in, chat messages).  
- Zod schemas are tested to ensure proper validation.

### 8.3 End-to-End Testing
- Playwright or Cypress for full scenarios: sign-in, theme toggle, AI chat cycle.  

### 8.4 Linting & Formatting
- ESLint (with TypeScript rules) enforces code style and catches errors early.  
- Prettier handles consistent formatting.  
- Husky + lint-staged run checks on pre-commit.

## 9. Conclusion and Overall Frontend Summary
This frontend setup combines Next.js, TypeScript, Tailwind CSS v4, shadcn/ui, Clerk, Supabase, and the Vercel AI SDK into a cohesive developer experience. It emphasizes:
- **Scalability** through modular, file-based structure.  
- **Maintainability** with clear patterns, typed components, and headless UI.  
- **Performance** via SSR, code splitting, and optimized assets.  
- **Accessibility and Usability** with consistent design tokens and ARIA-compliant components.

By following these guidelines, teams can confidently extend the starter kit, add new features, and maintain a high-quality, performant, and user-friendly application.