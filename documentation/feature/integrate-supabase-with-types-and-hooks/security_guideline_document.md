# Security Guidelines for CodeGuide Starter Kit Lite v2

## 1. Introduction
This document defines security requirements and best practices for the CodeGuide Starter Kit Lite v2, a Next.js 15 App Router template integrating Clerk, Supabase, Vercel AI SDK, TailwindCSS, shadcn/ui, and other third-party libraries. It guides developers to build a secure, resilient, and maintainable starter kit by design.

## 2. Core Security Principles
- **Security by Design:** Embed security from initial design through deployment.  
- **Least Privilege:** Grant only necessary permissions to services, users, and modules.  
- **Defense in Depth:** Layer controls so no single failure compromises the system.  
- **Fail Securely:** On errors or exceptions, avoid exposing sensitive data and maintain a secure state.  
- **Keep Security Simple:** Favor clear, maintainable controls over overly complex mechanisms.  
- **Secure Defaults:** Default configurations must favor security (e.g., HTTPS only, strict Content Security Policy).

## 3. Authentication & Access Control
1. **Clerk Integration:**  
   - Enforce strong password policies via Clerk (minimum length, complexity, history).  
   - Enable Multi-Factor Authentication (MFA) for sensitive accounts or admin roles.  
   - Use Clerk middleware (`middleware.ts`) to protect `/dashboard`, `/profile`, `/api/*`, and any RLS-protected routes.  
2. **Session Management:**  
   - Ensure session tokens are unpredictable and stored in Secure, HttpOnly, SameSite=Strict cookies.  
   - Implement idle and absolute timeouts. Invalidate sessions on logout.  
3. **Role-Based Access Control (RBAC):**  
   - Define roles (e.g., `user`, `admin`) and enforce server-side authorization checks in API routes and server components.  
   - Avoid client-side role checks as the sole authorization mechanism.

## 4. Input Handling & Output Encoding
1. **Server-Side Validation:**  
   - Validate every API payload (chat messages, user profiles, CRUD operations) using schemas (e.g., Zod).  
   - Reject or sanitize unexpected fields.  
2. **Prevent Injection:**  
   - Use Supabase client with prepared statements under the hood (no raw SQL queries).  
   - Never interpolate untrusted data into SQL/JS command strings.  
3. **Cross-Site Scripting (XSS):**  
   - Escape or sanitize all user-supplied content rendered in React (e.g., use `react-sanitize` or whitelist HTML).  
   - Implement a strict Content Security Policy (CSP) to restrict executable scripts.  
4. **Redirect Validation:**  
   - If any login redirect routes accept a `redirectTo` parameter, validate it against an allow-list of internal paths.

## 5. Data Protection & Privacy
1. **Encryption in Transit:**  
   - Enforce TLS 1.2+ on Vercel (HTTPS). Configure `next.config.js` to redirect all HTTP traffic to HTTPS.  
2. **Encryption at Rest:**  
   - Rely on Supabase’s built-in disk encryption.  
3. **Secrets Management:**  
   - Store all API keys and credentials (Clerk, Supabase, OpenAI, Anthropic) in environment variables or a secret manager (e.g., Vercel Environment Variables).  
   - Do not commit `.env.*` files or secrets to version control.  
4. **PII Handling:**  
   - Only capture necessary user data. Mask or redact sensitive fields in logs.  
   - Comply with GDPR/CCPA around user data deletion and export upon request.

## 6. API & Service Security
1. **Enforce HTTPS:**  
   - All API endpoints (`/api/chat`, Supabase endpoints) must be accessed only over TLS.  
2. **Rate Limiting & Throttling:**  
   - Implement edge rate limiting on chat API (e.g., Vercel Edge Middleware or third-party package) to mitigate brute-force or DoS attempts.  
3. **CORS Configuration:**  
   - Restrict cross-origin requests in `next.config.js` or API route middleware to only your deployed front-end origins.  
4. **Minimal Data Exposure:**  
   - API responses should include only necessary fields. Avoid returning internal IDs, secrets, or stack traces.

## 7. Web Application Security Hygiene
1. **CSRF Protection:**  
   - For any state-changing POST/PUT/DELETE endpoints, implement anti-CSRF tokens (Next.js built-in or `csurf`).  
2. **Security Headers:**  
   - Configure in `next.config.js` or custom server headers:  
     - `Content-Security-Policy` (restrict scripts, styles, frames).  
     - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`.  
     - `X-Content-Type-Options: nosniff`.  
     - `X-Frame-Options: DENY`.  
     - `Referrer-Policy: strict-origin-when-cross-origin`.  
3. **Secure Cookies:**  
   - Set `Secure`, `HttpOnly`, and `SameSite=Strict` for session cookies.  
4. **Subresource Integrity (SRI):**  
   - If loading any third-party scripts or styles via CDN, use integrity hashes.

## 8. Infrastructure & Configuration Management
1. **Production vs. Development:**  
   - Disable Next.js’s React developer tools and verbose logging in production.  
   - Ensure `NODE_ENV=production` on deployment.  
2. **Server Hardening:**  
   - On any custom servers, disable unused ports and services, enforce OS-level permissions.  
3. **Environment Variable Checks:**  
   - Implement runtime checks (in `lib/env.ts`) to fail build/start if required vars are missing.  
4. **TLS Configuration:**  
   - Use Vercel’s managed certificates or enforce Let’s Encrypt with strong cipher suites.

## 9. Dependency Management
1. **Secure Dependencies:**  
   - Vet all npm packages (shadcn/ui, clsx, date-fns, etc.) for active maintenance and known vulnerabilities.  
2. **Lockfiles & SCA Tools:**  
   - Commit `package-lock.json` or `yarn.lock`.  
   - Integrate automated vulnerability scanning (e.g., GitHub Dependabot, Snyk).  
3. **Minimize Footprint:**  
   - Remove unused dependencies; audit transitive dependencies regularly.

## 10. Monitoring & Incident Response
- **Logging & Alerts:**  
  - Centralize logs (Vercel logs, Supabase logs). Mask PII.  
  - Configure alerts for unusual authentication failures or rate-limit breaches.  
- **Error Handling:**  
  - Catch and handle exceptions in API routes; return generic error messages to clients.  
  - Log detailed errors internally (without sensitive context).
- **Regular Reviews:**  
  - Conduct periodic security audits and dependency vulnerability checks.  
  - Update security policies based on new threats and project scope changes.

---
Adherence to these guidelines will ensure that the CodeGuide Starter Kit Lite v2 is secure by default, simplifying the path for developers to build robust applications on top of it. Regularly review and update this document to incorporate emerging best practices and address newly discovered vulnerabilities.