# 🗺️ Viaggiamo Frontend - URL & Routing Guide

## Complete URL Structure & Navigation Reference

This guide documents all URLs, routes, and navigation in the Viaggiamo frontend following Next.js App Router conventions.

## 📍 URL Mapping (After Refactoring)

### ✅ Existing Routes

| URL | File Path | Description | Auth Required |
|-----|-----------|-------------|---------------|
| `/` | `app/page.tsx` | Homepage | No |
| `/login` | `app/(auth)/login/page.tsx` | Login page | No |
| `/register` | `app/(auth)/register/page.tsx` | Register page | No |
| `/dashboard` | `app/(protected)/dashboard/page.tsx` | User dashboard | ✅ Yes |
| `/profile` | `app/(protected)/profile/page.tsx` | User profile | ✅ Yes |

### ❌ Referenced but Not Created Yet

| URL | Component Referencing It | Purpose | Auth Required |
|-----|-------------------------|---------|---------------|
| `/trips` | NavBar, Footer, Hero, QuickActions | Search trips | No |
| `/trips/create` | NavBar, Footer, Hero, QuickActions | Create trip | ✅ Yes |
| `/my-trips` | NavBar | User's trips | ✅ Yes |
| `/about` | NavBar, Footer | About page | No |
| `/help` | NavBar, Footer | Help center | No |
| `/safety` | Footer | Safety info | No |
| `/contact` | Footer | Contact | No |
| `/privacy` | Footer, Auth pages | Privacy policy | No |
| `/terms` | Footer, Auth pages | Terms of service | No |
| `/settings` | UserMenu | User settings | ✅ Yes |
| `/forgot-password` | Login page | Password reset | No |

## 🎯 Route Groups (Parentheses Don't Affect URLs!)

### (auth) - Authentication Routes

```
app/(auth)/
├── layout.tsx              # Auth-specific layout
├── loading.tsx             # Auth loading UI
├── error.tsx               # Auth error boundary
├── login/
│   ├── page.tsx           → URL: /login
│   └── loading.tsx        → Loading state for login
└── register/
    ├── page.tsx           → URL: /register
    └── loading.tsx        → Loading state for register
```

**Key Point:** URLs don't include `(auth)` - it's just for organization!

### (protected) - Protected Routes

```
app/(protected)/
├── layout.tsx              # Auth guard (auto-redirects)
├── loading.tsx             # Protected loading UI
├── error.tsx               # Protected error boundary
├── not-found.tsx           # Protected 404 page
├── dashboard/
│   ├── page.tsx           → URL: /dashboard
│   └── loading.tsx
└── profile/
    ├── page.tsx           → URL: /profile
    └── loading.tsx
```

**Benefits:**
- All routes in this group require authentication
- Shared layout handles redirect to `/login`
- No need to wrap each page with `<ProtectedRoute>`

## 📝 Navigation Components

### 1. **NavBar** - Main Navigation

**File:** `src/components/layout/NavBar/NavBar.tsx`

**Links when NOT logged in:**
```tsx
/about
/help
/trips/create
/login          ← Updated from /auth/login
/register       ← Updated from /auth/register
```

**Links when logged in:**
```tsx
/dashboard
/trips
/trips/create
/my-trips
```

### 2. **UserMenu** - User Dropdown

**File:** `src/components/layout/NavBar/UserMenu.tsx`

```tsx
/profile
/settings
logout (function)
```

### 3. **Footer** - Site Footer

**File:** `src/components/layout/Footer/Footer.tsx`

**Producto:**
```tsx
/trips
/trips/create
/about
```

**Soporte:**
```tsx
/help
/safety
/contact
```

**Legal:**
```tsx
/privacy
/terms
```

### 4. **Quick Actions** - Dashboard & Hero

**Dashboard:** `src/features/dashboard/components/QuickActions.tsx`
**Hero:** `src/features/home/components/HeroSection.tsx`

```tsx
/trips          # Search trips
/trips/create   # Create new trip
```

## 🔧 Configuration Files

### routes.ts - Centralized Route Constants

**File:** `src/config/routes.ts`

```tsx
export const ROUTES = {
  // Public
  HOME: '/',
  ABOUT: '/about',
  HELP: '/help',

  // Auth
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',

  // Protected
  DASHBOARD: '/dashboard',
  PROFILE: '/profile',
  SETTINGS: '/settings',

  // Trips
  TRIPS: '/trips',
  TRIPS_CREATE: '/trips/create',
  MY_TRIPS: '/my-trips',
  TRIP_DETAIL: (id) => `/trips/${id}`,

  // Bookings
  MY_BOOKINGS: '/bookings',
  BOOKING_DETAIL: (id) => `/bookings/${id}`,
}
```

**Usage:**
```tsx
import { ROUTES } from '@/config/routes'

router.push(ROUTES.DASHBOARD)  // Type-safe!
<Link href={ROUTES.LOGIN}>Login</Link>
```

**Benefits:**
- ✅ Autocomplete in IDE
- ✅ Type checking
- ✅ Single source of truth
- ✅ Easy to refactor
- ✅ No typos in routes

### Helper Functions

```tsx
isProtectedRoute(pathname)  // Check if route requires auth
isAuthRoute(pathname)       // Check if route is auth-related
```

## 🛡️ Route Protection

### Multi-Layer Protection

1. **Middleware (Server-Side)**
   ```tsx
   // src/middleware.ts
   // Runs BEFORE the page loads
   // Checks cookie/token
   // Fast redirect
   ```

2. **Layout (Client-Side)**
   ```tsx
   // app/(protected)/layout.tsx
   // Checks AuthContext
   // Redirects if no user
   // Shows loading while checking
   ```

3. **Route Group Organization**
   ```tsx
   // All routes in (protected)/ are guarded
   // No manual wrapper needed
   ```

## 🎨 Special Route Files

### Loading States

Every route can have a loading UI:

```tsx
// app/(protected)/dashboard/loading.tsx
export default function DashboardLoading() {
  return <SkeletonUI />
}
```

**Shows automatically** while `page.tsx` loads!

### Error Boundaries

Catch errors at any level:

```tsx
// app/(protected)/error.tsx
'use client'  // Must be client component

export default function ProtectedError({ error, reset }) {
  return (
    <div>
      <h1>Error: {error.message}</h1>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Not Found Pages

Custom 404 for each section:

```tsx
// app/(protected)/not-found.tsx
export default function ProtectedNotFound() {
  return <Custom404ForProtectedRoutes />
}
```

## 📊 Route Hierarchy

```
Root Layout (app/layout.tsx)
├── Applies to: ALL routes
├── Provides: AuthProvider, Toaster, Global styles
│
├─┬─ Auth Layout (app/(auth)/layout.tsx)
│ └── Applies to: /login, /register
│     └── Provides: Auth-specific metadata
│
└─┬─ Protected Layout (app/(protected)/layout.tsx)
  └── Applies to: /dashboard, /profile, /settings, etc.
      └── Provides: Auth guard, auto-redirect
```

## 🔄 Navigation Flow

### Registration → Login → Dashboard

```
User on /
  ↓ Clicks "Crear Cuenta"
/register
  ↓ Google SSO or Email form
Registration success
  ↓ Redirect
/login
  ↓ Enter credentials
Login success
  ↓ Redirect
/dashboard (protected)
```

### Homepage Adaptive Behavior

```tsx
// app/page.tsx
const { user } = useAuth()

<HeroSection user={user} />
// If user: Shows "Welcome back" + quick actions
// If no user: Shows search form
```

### Profile Access

```
User logged in
  ↓ Clicks avatar in NavBar
UserMenu dropdown appears
  ↓ Clicks "Mi Perfil"
/profile (protected)
```

### Logout Flow

```
User clicks "Cerrar Sesión"
  ↓
AuthContext.logout()
  ↓ Clears token, updates state
Redirect to /
```

## 🚀 Adding New Routes

### Public Route

```tsx
// 1. Create page
// app/about/page.tsx
export default function AboutPage() {
  return <div>About Us</div>
}

// 2. Add to ROUTES constant
// config/routes.ts
export const ROUTES = {
  ABOUT: '/about',
}

// 3. Use it
import { ROUTES } from '@/config/routes'
<Link href={ROUTES.ABOUT}>About</Link>
```

### Protected Route

```tsx
// 1. Create inside (protected)/ group
// app/(protected)/settings/page.tsx
export default function SettingsPage() {
  return <div>Settings</div>
}

// 2. Protection is AUTOMATIC via layout!

// 3. Optional: Add loading state
// app/(protected)/settings/loading.tsx
export default function SettingsLoading() {
  return <Skeleton />
}
```

### Dynamic Route

```tsx
// app/(protected)/trips/[id]/page.tsx
export default function TripDetailPage({ params }: { params: { id: string } }) {
  return <div>Trip {params.id}</div>
}

// Usage:
<Link href={`/trips/${tripId}`}>View Trip</Link>

// Or with helper:
<Link href={ROUTES.TRIP_DETAIL(tripId)}>View Trip</Link>
```

## 🔍 Finding a Route

Use the ROUTES constant:

```tsx
import { ROUTES } from '@/config/routes'

// All routes available with autocomplete:
ROUTES.HOME
ROUTES.LOGIN
ROUTES.DASHBOARD
ROUTES.PROFILE
// etc...
```

## 📱 SEO & PWA

### Automatically Generated

- `/manifest.json` - PWA manifest (from `app/manifest.ts`)
- `/robots.txt` - Robots file (from `app/robots.ts`)
- `/sitemap.xml` - Sitemap (from `app/sitemap.ts`)

### Per-Page Metadata

```tsx
// app/(protected)/dashboard/page.tsx
export const metadata = {
  title: 'Dashboard',  // Becomes "Dashboard | Viaggiamo"
  description: 'User dashboard',
}
```

## 📚 Navigation API

### useRouter (Client)

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { ROUTES } from '@/config/routes'

const router = useRouter()
router.push(ROUTES.DASHBOARD)    // Navigate
router.refresh()                  // Refresh data
router.back()                     // Go back
```

### Link Component

```tsx
import Link from 'next/link'
import { ROUTES } from '@/config/routes'

<Link href={ROUTES.PROFILE}>Profile</Link>
```

### Programmatic Redirect

```tsx
import { redirect } from 'next/navigation'

// In Server Component or Server Action
redirect(ROUTES.LOGIN)
```

## ✅ Best Practices Followed

1. ✅ **Route Groups** for organization without URL impact
2. ✅ **Nested Layouts** for shared UI and logic
3. ✅ **Loading States** for better UX
4. ✅ **Error Boundaries** for graceful failures
5. ✅ **Centralized Routes** for maintainability
6. ✅ **Middleware** for server-side protection
7. ✅ **Dynamic Metadata** for SEO
8. ✅ **Special Files** (manifest, robots, sitemap)
9. ✅ **Server/Client Separation** where appropriate
10. ✅ **TypeScript** for type safety

## 🎉 Result

Your routing is now:
- ✨ **Cleaner** - `/login` instead of `/auth/login`
- 🎯 **Type-Safe** - ROUTES constant with autocomplete
- 🛡️ **Protected** - Multi-layer auth protection
- 📱 **SEO-Ready** - Dynamic sitemap, robots, manifest
- 🎨 **UX-Optimized** - Loading states everywhere
- 🐛 **Resilient** - Error boundaries at every level
- 📖 **Maintainable** - Following Next.js conventions

---

**All routes follow Next.js best practices! 🚀**

_Reference: [Next.js App Router Routing](https://nextjs.org/docs/app/building-your-application/routing)_
