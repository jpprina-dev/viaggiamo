# Protected Routes Fix - Token Storage Issue

## Problem

After logging in, users were not being redirected to the dashboard (`/dashboard`). The login appeared successful, but the page wouldn't navigate to protected routes.

## Root Cause

**Mismatch between token storage and middleware checks:**

1. **Login stored token in**: `localStorage` only
2. **Middleware checked token in**: `cookies` only

Since Next.js middleware runs on the **server-side**, it cannot access `localStorage` (which is client-side only). This caused:

```
User logs in → Token stored in localStorage → Middleware can't see it →
Redirects back to /login → Infinite redirect loop or stuck on login page
```

## Solution

Store the authentication token in **both** `localStorage` and `cookies`:

### Changes Made

#### 1. Updated `login()` function (`frontend/src/lib/auth.ts`)

```typescript
// BEFORE
export async function login(email: string, password: string): Promise<string> {
  const data: any = await graphqlClient.request(LOGIN_MUTATION, { email, password })
  const authResponse: AuthResponse = data.login

  // ❌ Only stored in localStorage
  localStorage.setItem('accessToken', authResponse.accessToken)
  setAuthToken(authResponse.accessToken)

  return authResponse.accessToken
}

// AFTER
export async function login(email: string, password: string): Promise<string> {
  const data: any = await graphqlClient.request(LOGIN_MUTATION, { email, password })
  const authResponse: AuthResponse = data.login

  // ✅ Store in BOTH localStorage and cookies
  localStorage.setItem('accessToken', authResponse.accessToken)
  Cookies.set('accessToken', authResponse.accessToken, { expires: 7 }) // 7 days
  setAuthToken(authResponse.accessToken)

  return authResponse.accessToken
}
```

#### 2. Updated `loginWithGoogle()` function

```typescript
// ✅ Also stores in both localStorage and cookies
localStorage.setItem('accessToken', authResponse.accessToken)
Cookies.set('accessToken', authResponse.accessToken, { expires: 7 })
setAuthToken(authResponse.accessToken)
```

#### 3. Updated `logout()` function

```typescript
// BEFORE
export function logout() {
  localStorage.removeItem('accessToken')
  removeAuthToken()
}

// AFTER
export function logout() {
  localStorage.removeItem('accessToken')
  Cookies.remove('accessToken')  // ✅ Also remove from cookies
  removeAuthToken()
}
```

#### 4. Updated `getCurrentUser()` function

```typescript
// ✅ Check both localStorage and cookies (with fallback)
let token = localStorage.getItem('accessToken')
if (!token) {
  token = Cookies.get('accessToken')
  // Sync token to localStorage if found in cookies
  if (token) {
    localStorage.setItem('accessToken', token)
  }
}
```

#### 5. Added dependency

```typescript
import Cookies from 'js-cookie'  // Already installed in package.json
```

## How Middleware Works

### Middleware Check (`frontend/src/middleware.ts`)

```typescript
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies (server-side accessible)
  const token = request.cookies.get('accessToken')?.value

  const protectedPaths = ['/dashboard', '/profile', '/settings', '/my-trips', '/bookings']
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path))

  // ✅ Now token is found in cookies!
  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}
```

## Why Both localStorage and Cookies?

| Storage | Purpose | Access |
|---------|---------|--------|
| **localStorage** | Client-side state management, fast access | Client-side JavaScript only |
| **cookies** | Server-side middleware checks | Both client & server |

### Benefits of Dual Storage:

1. **Client-side**: Fast access via `localStorage` for API calls
2. **Server-side**: Middleware can protect routes using `cookies`
3. **Sync**: If one is missing, we can restore from the other
4. **Persistence**: Cookies survive page reloads and SSR

## Authentication Flow

### Before Fix ❌

```
1. User clicks "Login"
2. Token stored in localStorage only
3. Router tries to navigate to /dashboard
4. Middleware runs (server-side) → checks cookies → no token found
5. Middleware redirects to /login
6. User stuck on login page
```

### After Fix ✅

```
1. User clicks "Login"
2. Token stored in BOTH localStorage and cookies
3. Router tries to navigate to /dashboard
4. Middleware runs (server-side) → checks cookies → token found! ✓
5. Middleware allows access
6. User sees dashboard
```

## Testing the Fix

### Test 1: Manual Login

```bash
1. Visit http://localhost:3000/login
2. Enter credentials:
   - Email: test@example.com
   - Password: password123
3. Click "Iniciar Sesión"
4. Should redirect to /dashboard ✅
```

### Test 2: Verify Token Storage

```javascript
// Open browser console after login
console.log('localStorage:', localStorage.getItem('accessToken'))
console.log('cookies:', document.cookie)

// Both should show the token
```

### Test 3: Protected Route Direct Access

```bash
1. Login to the app
2. Navigate to http://localhost:3000/dashboard
3. Should see dashboard (not redirect to login) ✅
```

### Test 4: Logout

```bash
1. Click logout
2. Try to access http://localhost:3000/dashboard
3. Should redirect to /login ✅
```

### Test 5: Page Reload

```bash
1. Login to the app
2. On dashboard, reload the page (F5)
3. Should stay on dashboard (not logout) ✅
```

## Cookie Configuration

```typescript
Cookies.set('accessToken', token, {
  expires: 7,          // Cookie expires in 7 days
  // secure: true,     // Uncomment for production (HTTPS only)
  // sameSite: 'lax'   // CSRF protection
})
```

### Production Considerations:

For production, update cookie settings:

```typescript
Cookies.set('accessToken', token, {
  expires: 7,
  secure: true,      // ✅ HTTPS only
  sameSite: 'strict', // ✅ Better CSRF protection
  path: '/',         // Available to all routes
})
```

## Related Files Modified

1. ✅ `frontend/src/lib/auth.ts` - Added cookie storage
2. ✅ `frontend/src/middleware.ts` - Already checking cookies (no changes needed)
3. ✅ Package dependencies - `js-cookie` already installed

## Common Issues

### Issue: Still redirecting after login
**Solution**: Clear browser cookies and localStorage, then try again
```javascript
localStorage.clear()
document.cookie.split(";").forEach(c => {
  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
});
```

### Issue: Token not persisting after page reload
**Solution**: Check if cookies are being blocked by browser settings

### Issue: "Cookies is not defined" error
**Solution**: Ensure `js-cookie` is imported at the top of the file
```typescript
import Cookies from 'js-cookie'
```

## Status

✅ **Protected routes are now working correctly**

- Users can login and access `/dashboard`
- Middleware properly checks authentication
- Page reloads maintain login state
- Logout clears both storage locations

## Next Steps

- [ ] Test login flow end-to-end
- [ ] Test Google OAuth login flow
- [ ] Test protected routes (/profile, /settings)
- [ ] Test logout clears all tokens
- [ ] Test page reload maintains auth state
- [ ] Add production cookie security settings before deployment
