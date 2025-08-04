# Git-Search Security Guidelines

This document provides actionable, project-specific security guidance for the **git-search** repository, following “secure by design” principles. It covers authentication, data protection, API hardening, deployment, and ongoing practices to ensure robust security throughout the application lifecycle.

---

## 1. Security by Design & Governance

- Embed security reviews in every sprint: include threat modeling when adding new features (e.g., AI chat, favorites).
- Define security owners for authentication, data handling, and deployment pipelines.
- Enforce least privilege at every layer: code, database, cloud functions.
- Automate checks using CI/CD: linting, SCA (Software Composition Analysis), static analysis (e.g., ESLint with security rules, Snyk).

## 2. Authentication & Access Control

1. **Clerk Configuration**
   - Enforce strong password complexity and rotation policies.
   - Enable multi-factor authentication (MFA) for all user accounts.
   - Validate JWTs server-side: check `alg`, `iss`, `aud`, and expiration (`exp`).

2. **Session & Cookie Security**
   - Use `Secure`, `HttpOnly`, and `SameSite=Strict` on session cookies.
   - Implement idle and absolute session timeouts; provide explicit logout endpoint.
   - Protect API routes against session fixation by regenerating session IDs on login.

3. **Role-Based Access Control (RBAC)**
   - Define roles (e.g., `guest`, `user`, `admin`) and map permissions explicitly in middleware (`src/middleware.ts`).
   - Enforce server-side checks on all protected routes: `/dashboard`, `/favorites`, `/api/github/favorites`.
   - Use Supabase Row-Level Security (RLS) to isolate user data; review policies regularly.

## 3. Input Validation & Output Encoding

- Use a runtime schema library (e.g., Zod) to validate all API inputs:
  * Query parameters (`/api/github/search?query=`)
  * Dynamic path segments (`/[owner]/[repo]`)
  * Request bodies for chat, favorites, and analysis endpoints.
- Sanitize outputs rendered in React components; avoid `dangerouslySetInnerHTML`. When necessary, whitelist tags and attributes.
- Prevent injection in Supabase queries by using the official client library and parameterized calls—never concatenate SQL strings.
- Validate and whitelist redirect URLs to avoid open-redirect attacks.

## 4. Data Protection & Privacy

- Enforce TLS 1.2+ on all Next.js serverless functions and web traffic. Do not allow HTTP.
- **Environment secrets**:
  * Store Clerk API keys, Supabase credentials, and GitHub tokens in Vercel Environment Variables or a secrets manager (e.g., AWS Secrets Manager, Vault).
  * Use `lib/env-check.ts` to fail startup if required variables are missing.
- Avoid logging sensitive PII or raw tokens. Mask or redact values in logs.
- For personally identifiable information (e.g., user email), comply with GDPR/CCPA:
  * Provide deletion endpoints.
  * Log consent.

## 5. API & Service Security

1. **Rate Limiting & Throttling**
   - Implement per-IP and per-user rate limits on critical endpoints (`/api/github/*`, `/api/chat`).
   - Use an in-memory or Redis cache layer for ephemeral rate counters.

2. **CORS Configuration**
   - Restrict `Access-Control-Allow-Origin` to your production and staging domains only.

3. **Least Privilege for API Keys**
   - Create a GitHub App or fine-scoped personal access token limited to read-only repository search and metadata.
   - Scope Supabase service roles to only the required tables and operations.

4. **API Versioning**
   - Prefix internal API routes with version numbers (e.g., `/api/v1/github/search`) to manage future changes securely.

## 6. Web Application Security Hygiene

- **Content Security Policy (CSP):**
  * Default to `self` for scripts, styles, and connect endpoints.
  * Allow only the AI service domains (OpenAI, Anthropic) and GitHub API in `connect-src`.
- **Security Headers:**
  * `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  * `X-Frame-Options: DENY`
  * `X-Content-Type-Options: nosniff`
  * `Referrer-Policy: no-referrer-when-downgrade`
- **CSRF Protection:**
  * Use anti-CSRF tokens (synchronizer token pattern) on state-changing forms and fetch calls.
- **Subresource Integrity (SRI):**
  * When loading third-party scripts (e.g., analytics), include integrity hashes and `crossorigin` attributes.

## 7. Infrastructure & Configuration Management

- **Vercel & Docker**:
  * Disable Next.js debugger and verbose logs in production builds (`NODE_ENV=production`).
  * Limit serverless function timeouts to prevent DoS amplification.
- **Server Hardening**:
  * Disable unnecessary ports and services on any custom servers.
  * Use up-to-date TLS cipher suites (ECDHE, AES-GCM) and disable TLS 1.0/1.1.
- **File Permissions**:
  * Ensure uploaded files (if any) are stored outside the webroot with restricted filesystem permissions.

## 8. Dependency Management

- Maintain `package-lock.json` to freeze known-good versions.
- Regularly run automated vulnerability scans (e.g., `npm audit`, Snyk) and update dependencies.
- Vet all major framework upgrades (Next.js, Tailwind, Clerk, Supabase, Octokit) for breaking changes and security fixes.
- Remove unused packages to minimize attack surface.

## 9. DevOps & CI/CD Security

- Enforce branch protection and require PR reviews before merging.
- Integrate static analysis tools:
  * ESLint with security plugins (e.g., eslint-plugin-security).
  * Secrets scanning in CI (e.g., GitHub Secret Scanning).
- Automate deployments only from the `main` branch; require successful tests and security checks.

## 10. Monitoring, Logging & Incident Response

- Integrate an error-tracking service (Sentry, LogRocket) for both serverless functions and client-side exceptions.
- Log all authentication events (login, logout, token refresh), but avoid storing raw tokens.
- Define an incident response plan: triage, notification, and post-mortem for security events.

---

By following these project-tailored guidelines, the **git-search** application will maintain strong defenses against common threats, safeguard user data, and uphold best practices for secure web development.  Regularly revisit this document as the codebase and threat landscape evolve.  
