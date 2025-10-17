# Next.js Best Practices - Frontend Structure

## ✅ Refactored to Follow Next.js Official Guidelines

This frontend now follows the [Next.js App Router best practices](https://nextjs.org/docs/app/getting-started/project-structure) with route groups, proper layouts, and special route files.

## 📁 New App Directory Structure

```
src/app/
│
├── layout.tsx                    # Root layout (all routes)
├── page.tsx                      # Homepage (/)
├── loading.tsx                   # Global loading UI
├── error.tsx                     # Global error boundary
├── not-found.tsx                 # Global 404 page
├── global-error.tsx              # Critical error boundary
├── manifest.ts                   # PWA manifest (dynamic)
├── robots.ts                     # Robots.txt (dynamic)
├── sitemap.ts                    # Sitemap.xml (dynamic)
├── globals.css                   # Global styles
│
├── (auth)/                       # 🔒 Auth route group
│   ├── layout.tsx               # Auth-specific layout
│   ├── loading.tsx              # Auth loading state
│   ├── error.tsx                # Auth error boundary
│   ├── login/
│   │   ├── page.tsx            # /login (not /auth/login)
│   │   └── loading.tsx         # Login loading state
│   └── register/
│       ├── page.tsx            # /register (not /auth/register)
│       └── loading.tsx         # Register loading state
│
└── (protected)/                  # 🛡️ Protected route group
    ├── layout.tsx               # Auth guard + loading
    ├── loading.tsx              # Protected loading state
    ├── error.tsx                # Protected error boundary
    ├── not-found.tsx            # Protected 404 page
    ├── dashboard/
    │   ├── page.tsx            # /dashboard
    │   └── loading.tsx         # Dashboard loading
    └── profile/
        ├── page.tsx            # /profile
        └── loading.tsx         # Profile loading
```

## 🎯 Key Next.js Conventions Implemented

### 1. **Route Groups** (Parentheses)

Route groups organize routes without affecting the URL structure:

```
app/
├── (auth)/
│   ├── login/page.tsx     → URL: /login  (NOT /auth/login)
│   └── register/page.tsx  → URL: /register
└── (protected)/
    ├── dashboard/page.tsx → URL: /dashboard
    └── profile/page.tsx   → URL: /profile
```

**Benefits:**
- ✅ Organize related routes together
- ✅ Apply specific layouts to route groups
- ✅ Parentheses don't appear in URLs
- ✅ Easier to manage auth vs protected routes

### 2. **Special Route Files**

| File | Purpose | Level |
|------|---------|-------|
| `layout.tsx` | Wraps all child routes | All levels |
| `page.tsx` | Renders the actual page | Required for routes |
| `loading.tsx` | Loading UI (Suspense fallback) | Optional |
| `error.tsx` | Error boundary | Optional |
| `not-found.tsx` | 404 page | Optional |
| `global-error.tsx` | Critical error recovery | Root only |

### 3. **Loading States** (Suspense Boundaries)

Automatic loading states with `loading.tsx`:

```tsx
// app/(protected)/dashboard/loading.tsx
export default function DashboardLoading() {
  return <SkeletonUI />
}
```

When navigating to `/dashboard`, Next.js automatically shows this loading UI while the page loads.

### 4. **Error Boundaries**

Graceful error handling with `error.tsx`:

```tsx
// app/(protected)/error.tsx
'use client'  // Must be client component

export default function ProtectedError({ error, reset }) {
  return (
    <div>
      <h1>Something went wrong</h1>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### 5. **Layouts Hierarchy**

```
Root Layout (app/layout.tsx)
└── Applies to ALL routes
    ├── Auth Layout (app/(auth)/layout.tsx)
    │   └── Only applies to /login, /register
    └── Protected Layout (app/(protected)/layout.tsx)
        └── Only applies to /dashboard, /profile
```

**Layout Features:**
- Layouts persist across navigation (don't re-render)
- Can be nested
- Share UI (NavBar, Footer, etc.)
- Maintain state

### 6. **Metadata Configuration**

#### Root Layout
```tsx
// app/layout.tsx
export const metadata: Metadata = {
  title: {
    default: 'Viaggiamo',
    template: '%s | Viaggiamo',  // Page titles use template
  },
}
```

#### Individual Pages
```tsx
// app/(auth)/login/page.tsx
export const metadata: Metadata = {
  title: 'Login',  // Becomes "Login | Viaggiamo"
  description: 'Log in to your account',
}
```

### 7. **Server vs Client Components**

**Server Components (default):**
- Layouts (`layout.tsx`)
- Static pages
- Metadata files (`manifest.ts`, `robots.ts`, `sitemap.ts`)

**Client Components (`'use client'`):**
- Interactive components
- useState, useEffect hooks
- Event handlers
- Browser APIs

### 8. **Middleware for Route Protection**

```tsx
// src/middleware.ts
export function middleware(request: NextRequest) {
  // Check authentication
  // Redirect if needed
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}
```

**Runs before:**
- Every route
- Centralized auth logic
- Automatic redirects

## 🗺️ Route Mapping

### Route Groups → URLs

| Route Group | File Path | Actual URL |
|-------------|-----------|------------|
| `(auth)/login` | `app/(auth)/login/page.tsx` | `/login` |
| `(auth)/register` | `app/(auth)/register/page.tsx` | `/register` |
| `(protected)/dashboard` | `app/(protected)/dashboard/page.tsx` | `/dashboard` |
| `(protected)/profile` | `app/(protected)/profile/page.tsx` | `/profile` |

**Note:** The parentheses `()` are removed from the URL path!

## 🔧 Configuration Files

### `/src/config/routes.ts` - Centralized Routes
```tsx
export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  // ...
}

// Usage
router.push(ROUTES.DASHBOARD)
```

**Benefits:**
- ✅ Single source of truth
- ✅ TypeScript autocomplete
- ✅ Easy to refactor
- ✅ Type-safe routing

### `/src/config/metadata.ts` - Shared Metadata
```tsx
export const sharedMetadata: Metadata = {
  // Common SEO tags
  // OpenGraph
  // Twitter cards
}

export function createPageMetadata(params) {
  // Helper to create page-specific metadata
}
```

### `/src/middleware.ts` - Route Protection
```tsx
export function middleware(request: NextRequest) {
  // Runs on every request
  // Auth checks
  // Redirects
}
```

## 📊 File Conventions Summary

### Required Files
- ✅ `app/layout.tsx` - Root layout
- ✅ `app/page.tsx` - Homepage

### Special Files (All Optional but Recommended)
- ✅ `loading.tsx` - Loading UI
- ✅ `error.tsx` - Error boundaries
- ✅ `not-found.tsx` - 404 pages
- ✅ `global-error.tsx` - Critical errors
- ✅ `manifest.ts` - PWA manifest
- ✅ `robots.ts` - SEO robots.txt
- ✅ `sitemap.ts` - SEO sitemap
- ✅ `middleware.ts` - Request middleware

### Naming Conventions
- `page.tsx` - Routes
- `layout.tsx` - Layouts
- `loading.tsx` - Loading states
- `error.tsx` - Error boundaries
- `not-found.tsx` - 404 pages
- `(folder)` - Route groups (don't affect URL)

## 🚀 Benefits of This Structure

### 1. **Better Organization**
```
(auth)/        → All auth pages together
(protected)/   → All protected pages together
```

### 2. **Automatic Features**
- Loading states without code
- Error boundaries without try/catch everywhere
- 404 pages per section

### 3. **Shared Layouts**
```tsx
// (auth)/layout.tsx applies to all auth pages
// (protected)/layout.tsx applies to all protected pages
// No need for wrapper components!
```

### 4. **Performance**
- Layouts don't re-render on navigation
- Automatic code splitting per route
- Streaming SSR with Suspense

### 5. **SEO**
- Dynamic sitemap.xml
- Dynamic robots.txt
- PWA manifest
- Proper metadata per page

### 6. **Developer Experience**
- Clear separation of concerns
- Type-safe routing with ROUTES constant
- Centralized middleware for auth
- Easy to add new routes

## 📝 Adding New Routes

### Public Route
```tsx
// 1. Create page
// app/about/page.tsx
export default function AboutPage() {
  return <div>About Us</div>
}

// 2. Add to routes config
// config/routes.ts
export const ROUTES = {
  ABOUT: '/about',
}
```

### Protected Route
```tsx
// 1. Create inside (protected)/ group
// app/(protected)/settings/page.tsx
export default function SettingsPage() {
  return <div>Settings</div>
}

// 2. Protection is automatic via layout!
```

### With Loading State
```tsx
// Create loading.tsx alongside page.tsx
// app/(protected)/settings/loading.tsx
export default function SettingsLoading() {
  return <div>Loading settings...</div>
}
```

## 🔄 Migration Summary

### What Changed
- ✅ Moved auth routes into `(auth)/` group
- ✅ Moved protected routes into `(protected)/` group
- ✅ Added loading states to all routes
- ✅ Added error boundaries at all levels
- ✅ Created 404 pages
- ✅ Added middleware for auth protection
- ✅ Created dynamic sitemap/robots/manifest
- ✅ Centralized route configuration
- ✅ Updated all imports and navigation

### URL Changes
| Old Path | New Path | Notes |
|----------|----------|-------|
| `/auth/login` | `/login` | ✅ Cleaner URLs |
| `/auth/register` | `/register` | ✅ Cleaner URLs |
| Others | Same | No change |

### Code Changes
- All `router.push('/auth/login')` → `router.push(ROUTES.LOGIN)`
- All hardcoded paths → Use `ROUTES` constant
- Removed old ProtectedRoute wrapper → Use layout-based protection

## 📚 References

- [Next.js App Router](https://nextjs.org/docs/app)
- [Route Groups](https://nextjs.org/docs/app/building-your-application/routing/route-groups)
- [Loading UI](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming)
- [Error Handling](https://nextjs.org/docs/app/building-your-application/routing/error-handling)
- [Metadata](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

**Structure now follows Next.js best practices! 🎉**
