# Auth Pages Design

**Date:** 2026-04-12  
**Status:** Approved

---

## Context

The backend and auth infrastructure (interceptors, token service, middleware) are complete. The login view exists but uses unstyled raw inputs. The register view and form are empty stubs. This spec covers the UI implementation of both auth pages.

---

## Layout

Each view is self-contained — no shared `layout.tsx` for auth. Both `LoginView` and `RegisterView` render their own full-screen centered wrapper + card.

**Visual style:** Dark card with border on dark background.
- Background: `#111` (app default)
- Card: `background: #161616`, `border: 1px solid #2a2a2a`, `border-radius: 16px`, `padding: 36px`, `box-shadow: 0 8px 32px rgba(0,0,0,0.4)`
- Card width: `360px` (fixed), centered with `flex justify-center items-center w-screen h-screen`

---

## File Changes

### Modified files

```
src/features/public/auth/
├── views/
│   ├── login-view.tsx           # rewrite — add card wrapper styling
│   └── register-view.tsx        # implement (currently empty stub)
└── components/forms/
    ├── login-form/
    │   └── login-form.tsx       # rewrite — replace raw inputs with Controller + Input/PasswordInput
    └── register-form/
        └── register-form.tsx    # implement (fix filename typo: regsiter → register)

src/shared/configs/page.config.ts  # add REGISTER = '/auth/register' to PublicPage
```

---

## Page Config

Add to `PublicPage` in `src/shared/configs/page.config.ts`:

```ts
readonly REGISTER = `${this.AUTH}/register`
```

---

## Component Structure

### LoginView (SSR — no `'use client'`)

```
LoginView
  └── div (w-screen h-screen flex justify-center items-center)
      └── LoginForm  ← 'use client' boundary here
```

Accepts `ComponentProps<'div'>` for flexibility (existing pattern).

### RegisterView (SSR — no `'use client'`)

```
RegisterView
  └── div (w-screen h-screen flex justify-center items-center)
      └── RegisterForm  ← 'use client' boundary here
```

### LoginForm ('use client')

Card contents:
1. `Logo` — centered, `size="md"`
2. `Typography variant="h5"` — «Вход в аккаунт»
3. `<Link href={PUBLIC_PAGE.REGISTER}>` — «Нет аккаунта? Зарегистрируйтесь» (small, color `primary-500`)
4. `Controller` + `Input` — email (`type="email"`, `placeholder="Email"`, `error={fieldState.error?.message}`)
5. `Controller` + `PasswordInput` — password (`placeholder="Пароль"`, `error={fieldState.error?.message}`)
6. `Button` — «Войти» (`type="submit"`, `isLoading={isPending}`, `className="w-full"`)

State management: `react-hook-form` + `valibotResolver(LoginSchema)`. Mode: `onChange`.

On success: `tokenService.save(data.access_token)` (handled by `authQuery.login()` onSuccess), then `router.replace(DASHBOARD_PAGE.HOME)` + `toast.success('Добро пожаловать')`.

On error: `toast.error(extractError(error))`.

### RegisterForm ('use client')

Card contents:
1. `Logo` — centered, `size="md"`
2. `Typography variant="h5"` — «Создать аккаунт»
3. `<Link href={PUBLIC_PAGE.LOGIN}>` — «Уже есть аккаунт? Войти»
4. `Controller` + `Input` — full_name (`placeholder="Имя"`, `error={fieldState.error?.message}`)
5. `Controller` + `Input` — email (`type="email"`, `placeholder="Email"`, `error={fieldState.error?.message}`)
6. `Controller` + `PasswordInput` — password (`placeholder="Пароль"`, `error={fieldState.error?.message}`)
7. `Button` — «Зарегистрироваться» (`type="submit"`, `isLoading={isPending}`, `className="w-full"`)

State management: `react-hook-form` + `valibotResolver(RegisterSchema)`. Mode: `onChange`.

On success: `tokenService.save(data.access_token)` (handled by `authQuery.register()` onSuccess), then `router.replace(DASHBOARD_PAGE.HOME)` + `toast.success('Аккаунт создан')`.

On error: `toast.error(extractError(error))`.

---

## Form Pattern (both forms)

All fields use `<Controller>` for consistent API — no mix of `register` and `Controller`.

```tsx
<Controller
  name="email"
  control={control}
  render={({ field, fieldState }) => (
    <Input
      {...field}
      type="email"
      placeholder="Email"
      error={fieldState.error?.message}
    />
  )}
/>

<Controller
  name="password"
  control={control}
  render={({ field, fieldState }) => (
    <PasswordInput
      value={field.value}
      onChange={field.onChange}
      placeholder="Пароль"
      error={fieldState.error?.message}
    />
  )}
/>
```

Submit handler: `handleSubmit(submit)` called via `onSubmit` on the form element (not via `onClick` on button — fixes current pattern in LoginForm).

---

## UI Components Used

All from `src/shared/components/ui/` — no new components needed, no imports from UI kit package.

| Component | SSR | Usage |
|-----------|-----|-------|
| `Logo` | Yes | Brand mark at top of card |
| `Typography` | Yes | Card title (h5) |
| `Input` | Yes | Email, full_name fields |
| `PasswordInput` | No (client) | Password field |
| `Button` | Yes | Submit button |

Navigation links: Next.js `<Link>` with inline Tailwind styling — no need for additional component.

---

## What Is NOT Changing

- `auth.schema.ts` — schemas are complete
- `auth.types.ts` — types are complete
- `auth.service.ts` — service is complete
- `auth.query.ts` — mutations with onSuccess are complete
- `app/(public)/auth/login/page.tsx` — no changes needed
- `app/(public)/auth/register/page.tsx` — no changes needed
