# Frontend Modular Architecture

## 📁 Project Structure

The frontend has been completely modularized following industry best practices for React/Next.js applications. This structure separates concerns, improves maintainability, and enhances code reusability.

```
src/
├── app/                          # Next.js App Router (Pages)
│   ├── auth/
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/
│   ├── layout.tsx
│   ├── page.tsx                  # Home page
│   └── globals.css
│
├── components/                   # Shared Components
│   ├── ui/                      # Reusable UI Components
│   │   ├── Button/
│   │   │   ├── Button.tsx       # Button component with variants
│   │   │   └── index.ts
│   │   ├── Input/
│   │   │   ├── Input.tsx        # Input with label, error states
│   │   │   └── index.ts
│   │   ├── Card/
│   │   │   ├── Card.tsx         # Card container with variants
│   │   │   └── index.ts
│   │   ├── Badge/
│   │   │   ├── Badge.tsx        # Status badges
│   │   │   └── index.ts
│   │   └── index.ts             # Barrel export
│   │
│   ├── layout/                  # Layout Components
│   │   ├── NavBar/
│   │   │   ├── NavBar.tsx       # Main navigation
│   │   │   ├── NavLink.tsx      # Navigation link
│   │   │   ├── UserMenu.tsx     # User dropdown menu
│   │   │   ├── GuestLinks.tsx   # Guest navigation links
│   │   │   └── index.ts
│   │   ├── Footer/
│   │   │   ├── Footer.tsx       # Footer component
│   │   │   ├── FooterSection.tsx
│   │   │   ├── FooterLink.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   └── common/                  # Common Components
│       └── ProtectedRoute/
│           ├── ProtectedRoute.tsx
│           └── index.ts
│
├── features/                    # Feature Modules (Domain-Driven)
│   ├── auth/                   # Authentication Feature
│   │   └── components/
│   │       ├── LoginForm.tsx    # Login form logic
│   │       ├── RegisterForm.tsx # Registration form logic
│   │       ├── AuthLayout.tsx   # Auth pages layout
│   │       └── index.ts
│   │
│   ├── home/                   # Home Page Feature
│   │   └── components/
│   │       ├── HeroSection.tsx
│   │       ├── PopularTrips.tsx
│   │       ├── BenefitsSection.tsx
│   │       ├── CTASection.tsx
│   │       ├── StatsSection.tsx
│   │       ├── HowItWorksSection.tsx
│   │       └── index.ts
│   │
│   └── dashboard/              # Dashboard Feature
│       └── components/
│           ├── WelcomeCard.tsx
│           ├── QuickActions.tsx
│           ├── UserInfoCard.tsx
│           ├── StatsCards.tsx
│           └── index.ts
│
├── types/                      # TypeScript Type Definitions
│   ├── user.ts                 # User-related types
│   ├── trip.ts                 # Trip-related types
│   ├── booking.ts              # Booking-related types
│   └── index.ts
│
├── utils/                      # Utility Functions
│   └── cn.ts                   # Class name utility
│
├── lib/                        # External Libraries Integration
│   ├── auth.ts
│   └── graphql-client.ts
│
└── contexts/                   # React Contexts
    └── AuthContext.tsx

```

## 🎯 Architecture Principles

### 1. **Separation of Concerns**
- **UI Components** (`components/ui/`) - Pure presentational components
- **Layout Components** (`components/layout/`) - Page structure components
- **Feature Modules** (`features/`) - Domain-specific business logic
- **Types** (`types/`) - Centralized type definitions

### 2. **Component Organization**

#### UI Components (`components/ui/`)
Reusable, presentational components with:
- Multiple variants (e.g., button variants: primary, secondary, outline)
- Consistent API across components
- TypeScript interfaces for props
- No business logic

**Example:**
```tsx
import { Button, Input, Card } from '@/components/ui'

<Button variant="primary" size="lg">
  Click Me
</Button>
```

#### Layout Components (`components/layout/`)
Structure and navigation components:
- NavBar with modular sub-components
- Footer with sections
- Reusable across multiple pages

#### Feature Modules (`features/`)
Domain-driven organization:
- Each feature has its own components
- Feature-specific logic and state
- Can have hooks, utils, types within the feature

**Example:**
```tsx
// features/auth/components/LoginForm.tsx
// Contains login form logic, validation, submission
```

### 3. **Import Patterns**

#### Barrel Exports
Each directory has an `index.ts` for clean imports:
```tsx
// Instead of:
import Button from '@/components/ui/Button/Button'

// Use:
import { Button } from '@/components/ui'
```

#### Path Aliases
Using `@/` alias for absolute imports:
```tsx
import { NavBar } from '@/components/layout'
import { User } from '@/types'
import { cn } from '@/utils/cn'
```

## 📦 Component Categories

### UI Components
- **Button** - Multiple variants, sizes, loading states
- **Input** - Labels, errors, icons support
- **Card** - Container with variants (bordered, elevated)
- **Badge** - Status indicators with color variants

### Layout Components
- **NavBar** - Responsive navigation with user menu
- **Footer** - Multi-column footer with links
- **ProtectedRoute** - Auth guard wrapper

### Feature Components

#### Auth Feature
- **LoginForm** - Email/password login with validation
- **RegisterForm** - User registration with validation
- **AuthLayout** - Consistent layout for auth pages

#### Home Feature
- **HeroSection** - Hero with search functionality
- **PopularTrips** - Trip listing cards
- **BenefitsSection** - Feature highlights
- **CTASection** - Call-to-action banner
- **StatsSection** - Statistics display
- **HowItWorksSection** - Process explanation

#### Dashboard Feature
- **WelcomeCard** - User greeting with profile
- **QuickActions** - Action cards
- **UserInfoCard** - Account information
- **StatsCards** - User statistics

## 🔧 Utility Functions

### `cn()` - Class Name Utility
Combines multiple class names and handles conditionals:
```tsx
import { cn } from '@/utils/cn'

<div className={cn(
  'base-class',
  variant === 'primary' && 'primary-class',
  isActive && 'active-class'
)} />
```

## 📝 Type System

Centralized TypeScript types in `types/`:

```tsx
// types/user.ts
export interface User {
  id: number
  email: string
  username: string
  fullName: string
  // ...
}

// Usage
import type { User } from '@/types'
```

## 🚀 Benefits

1. **Maintainability** - Clear structure makes code easy to find and modify
2. **Reusability** - UI components can be used across features
3. **Scalability** - Add new features without affecting existing code
4. **Type Safety** - Centralized types prevent inconsistencies
5. **Developer Experience** - Clean imports and logical organization
6. **Testing** - Isolated components are easier to test
7. **Code Splitting** - Feature-based splitting improves performance

## 📚 Best Practices

1. **Component Files** - One component per file
2. **Barrel Exports** - Use index.ts for clean imports
3. **TypeScript** - Define interfaces for all props
4. **Naming** - Use PascalCase for components, camelCase for utilities
5. **Co-location** - Keep related files together (component + types + utils)
6. **Composition** - Build complex UIs from simple components
7. **Props Over Config** - Prefer props to configuration files

## 🔄 Migration Guide

If adding new features:

1. **Create feature directory**: `features/my-feature/`
2. **Add components**: `features/my-feature/components/`
3. **Export from index**: `features/my-feature/components/index.ts`
4. **Use in pages**: Import from `@/features/my-feature/components`

Example:
```tsx
// features/trips/components/TripCard.tsx
export function TripCard({ trip }: TripCardProps) {
  return <Card>...</Card>
}

// features/trips/components/index.ts
export { TripCard } from './TripCard'

// app/trips/page.tsx
import { TripCard } from '@/features/trips/components'
```

## 🎨 Styling

Using Tailwind CSS with utility-first approach:
- Component-level styles using className
- Consistent design system through tailwind.config.js
- Responsive design with Tailwind breakpoints

## 📖 Related Documentation

- [Next.js App Router](https://nextjs.org/docs/app)
- [React Component Patterns](https://reactpatterns.com/)
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
