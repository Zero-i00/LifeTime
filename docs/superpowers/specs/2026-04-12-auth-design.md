# Auth System Design

**Date:** 2026-04-12  
**Status:** Approved

---

## Context

The backend already implements JWT auth (FastAPI, RS256). The frontend has partial infrastructure: axios instances, AuthService, TanStack Query mutations. Missing: token storage, request interceptors, route protection middleware.

---

## Token Strategy

- **Access token** — returned in response body by backend (15 min TTL). Stored in a regular JS-accessible cookie via `js-cookie` (`tokenService`). Sent as `Authorization: Bearer` header via axios request interceptor.
- **Refresh token** — set as httpOnly cookie by backend automatically (30 days TTL). Browser sends it automatically on `withCredentials: true` requests. Never touched by frontend code directly.

---

## File Structure

### New files

```
frontend/src/
├── proxy.ts                                        # Next.js middleware (route dispatcher)
├── shared/
│   ├── services/
│   │   └── token.service.ts                       # js-cookie wrapper (singleton)
│   ├── middleware/
│   │   ├── protected.middleware.ts                # Guard for /dashboard, /admin
│   │   └── auth-page.middleware.ts                # Redirect if already logged in
│   ├── api/
│   │   └── queue/
│   │       └── refresh-token.queue.ts             # Parallel 401 queue + cross-tab lock
│   └── broadcasts/
│       └── auth.broadcast.ts                      # BroadcastChannel cross-tab sync
```

### Modified files

```
frontend/src/shared/api/interceptors/
├── root.interceptor.ts       # + request interceptor: attach Authorization header
└── auth.interceptor.ts       # + response interceptor: 401 → refresh → retry

frontend/src/shared/configs/
└── page.config.ts            # + AdminPage domain if needed

frontend/src/features/public/auth/
└── queries/auth.query.ts     # + onSuccess: tokenService.save(); onLogout: tokenService.remove()
```

---

## Layer Responsibilities

| Layer | File | Responsibility |
|-------|------|----------------|
| Middleware dispatcher | `proxy.ts` | Match routes, delegate to correct middleware |
| Route guard | `shared/middleware/protected.middleware.ts` | Decode JWT → check exp → refresh or redirect |
| Auth page guard | `shared/middleware/auth-page.middleware.ts` | Redirect to dashboard if already authenticated |
| Token storage | `shared/services/token.service.ts` | CRUD access token in js-cookie (client only) |
| Request interceptor | `root.interceptor.ts` | Add `Authorization: Bearer <token>` to every request |
| 401 interceptor | `auth.interceptor.ts` | 401 → queue → refresh → retry all queued requests |
| Cross-tab queue | `shared/api/queue/refresh-token.queue.ts` | Single refresh across parallel requests + tabs |
| Cross-tab broadcast | `shared/broadcasts/auth.broadcast.ts` | BroadcastChannel for LOGOUT / REFRESH_SUCCESS / REFRESH_ERROR |
| Auth queries | `auth.query.ts` | Save/remove token on login/logout mutation callbacks |

---

## Data Flows

### Login

```
LoginForm
  → authQuery.login() mutation
  → AuthService.login() → POST /api/v1/auth/login
  → backend: access_token in body + refresh_token in httpOnly cookie
  → onSuccess: tokenService.save(access_token)
  → router.replace(DASHBOARD_PAGE.HOME)
```

### Navigation to protected route

```
Request /dashboard/*
  → proxy.ts (matcher matched)
  → protectedMiddleware(request)
      → request.cookies.get('access_token')
      → no cookie → redirect(PUBLIC_PAGE.LOGIN)
      → has cookie → decode base64 JWT payload → check exp
          → not expired → NextResponse.next()
          → expired → fetch(`${BACKEND_URL}/api/v1/auth/refresh_token`, { credentials: 'include' })
              → success → response.cookies.set('access_token', newToken) → NextResponse.next()
              → failure → redirect(PUBLIC_PAGE.LOGIN)
```

### Client API request with 401 handling

```
axiosAuth.get('/user/profile')
  → request interceptor: Authorization: Bearer <tokenService.get()>
  → 200 → data returned

  → 401 → auth.interceptor (response)
      → refreshTokenQueue.isRefreshing()?
          → yes → add to failedQueue, wait
          → no  → acquire localStorage lock
                 → AuthService.refresh() → POST /auth/refresh_token (httpOnly cookie sent auto)
                 → success:
                     tokenService.save(newToken)
                     authBroadcast.refreshSuccess()         → other tabs unblock
                     refreshTokenQueue.processSuccess()     → flush queue
                     release lock
                     retry original request
                 → failure:
                     authBroadcast.refreshError()
                     refreshTokenQueue.processError(err)
                     tokenService.remove()
                     router.replace(PUBLIC_PAGE.LOGIN)
```

### Logout

```
logout mutation
  → AuthService.logout() → POST /auth/logout
  → tokenService.remove()
  → authBroadcast.logout()
  → queryClient.clear()
  → router.replace(PUBLIC_PAGE.LOGIN)
```

---

## Edge Cases

### 1. Parallel 401s — single tab

`RefreshTokenQueue` (`shared/api/queue/refresh-token.queue.ts`):
- `failedQueue: QueuePromise[]` — blocked requests
- `refreshPromise: Promise | null` — active refresh indicator
- `isRefreshing()` — checks `refreshPromise || waitingForRemoteRefresh || isLockedByOtherTab()`
- `processSuccess()` — resolves all queued, clears queue
- `processError(err)` — rejects all queued, clears queue

Only the first 401 starts refresh. All others queue and retry after.

### 2. Parallel 401s — multiple tabs

**localStorage lock** (`refresh_token_lock`, timeout 10s):
- Tab that acquires lock performs refresh
- Other tabs see foreign lock → `waitingForRemoteRefresh = true`

**BroadcastChannel** (`auth_broadcast_channel`):
- Messages: `REFRESH_SUCCESS | REFRESH_ERROR | LOGOUT`
- Refreshing tab broadcasts result → waiting tabs call `processSuccess()` or `processError()`

### 3. Logout across tabs

Tab A logs out → broadcasts `LOGOUT` → Tab B (waiting on remote refresh) receives it → `processError()` → redirect to `PUBLIC_PAGE.LOGIN`.

### 4. Refresh token expired in middleware

`protectedMiddleware` → `fetch /auth/refresh_token` → backend returns 401 → `NextResponse.redirect(PUBLIC_PAGE.LOGIN)`.

### 5. TokenService — server context

`tokenService` (js-cookie) is client-only. Middleware reads tokens from `request.cookies` directly. `tokenService` is never called in server context.

### 6. Setting cookie after middleware refresh

Backend returns new `access_token` in response body. Middleware sets it via `response.cookies.set()` before `NextResponse.next()`. Backend updates httpOnly refresh cookie itself.

---

## Page Config

All route strings come from `shared/configs/page.config.ts`. No hardcoded path strings anywhere in auth code.

```ts
PUBLIC_PAGE.LOGIN       // redirect unauthenticated users
DASHBOARD_PAGE.HOME     // redirect after login / already authenticated
```

---

## What Is NOT Changing

- `AuthService` — nearly complete, one fix needed (see below)
- `axiosClient` / `axiosAuth` — base config unchanged, only interceptors added
- TanStack Query setup — only `auth.query.ts` callbacks updated

### AuthService.refresh() — fix required

`refresh()` must use `axiosClient` (no auth interceptor), not `axiosAuth`. Using `axiosAuth` creates infinite recursion: 401 on refresh → interceptor calls refresh → 401 again → loop.
