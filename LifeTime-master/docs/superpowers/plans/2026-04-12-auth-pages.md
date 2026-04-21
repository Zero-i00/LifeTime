# Auth Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement styled login and register pages using existing UI components, replacing bare raw inputs with proper Controller-based forms inside a dark card layout.

**Architecture:** Each view (SSR) renders a full-screen centered wrapper containing a client-side form component. All form fields use `<Controller>` from react-hook-form for a consistent API. Card styling is applied via Tailwind arbitrary values directly in the view — no new components needed.

**Tech Stack:** Next.js 16 App Router, react-hook-form + valibot, TanStack Query v5, Tailwind CSS v4, shared UI components (`Button`, `Input`, `PasswordInput`, `Typography`, `Logo`)

**Spec:** `docs/superpowers/specs/2026-04-12-auth-pages-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `src/shared/configs/page.config.ts` | Add `REGISTER` route constant |
| Rewrite | `src/features/public/auth/views/login-view.tsx` | Full-screen centered card wrapper |
| Implement | `src/features/public/auth/views/register-view.tsx` | Full-screen centered card wrapper |
| Rewrite | `src/features/public/auth/components/forms/login-form/login-form.tsx` | Controller-based login form |
| Create | `src/features/public/auth/components/forms/register-form/register-form.tsx` | Controller-based register form (fix filename typo) |
| Modify | `src/features/public/auth/components/forms/register-form/index.ts` | Export `RegisterForm` |
| Delete | `src/features/public/auth/components/forms/register-form/regsiter-form.tsx` | Remove old misnamed stub |

---

## Task 1: Add REGISTER to page config

**Files:**
- Modify: `src/shared/configs/page.config.ts`

- [ ] **Step 1: Add REGISTER constant**

Open `src/shared/configs/page.config.ts`. Current content:

```ts
class PublicPage {
    readonly HOME = '/'

    private readonly AUTH = `${this.HOME}/auth`
    readonly LOGIN = `${this.AUTH}/login`
    readonly REGISTER = `${this.AUTH}/register`
}
```

Wait — check the current file first. If `REGISTER` is already there, skip this task. If not, add it after `LOGIN`:

```ts
class PublicPage {
    readonly HOME = '/'

    private readonly AUTH = `${this.HOME}/auth`
    readonly LOGIN = `${this.AUTH}/login`
    readonly REGISTER = `${this.AUTH}/register`
}

class DashboardPage {
    readonly HOME = '/dashboard'

    readonly PROFILE = `${this.HOME}/profile`
}

export const PUBLIC_PAGE = new PublicPage()
export const DASHBOARD_PAGE = new DashboardPage()
```

- [ ] **Step 2: Commit**

```bash
git add src/shared/configs/page.config.ts
git commit -m "feat: add REGISTER route to PublicPage config"
```

---

## Task 2: Rewrite LoginView with card styling

**Files:**
- Rewrite: `src/features/public/auth/views/login-view.tsx`

- [ ] **Step 1: Replace login-view.tsx**

```tsx
import type { ComponentProps } from 'react'
import { twMerge } from 'tailwind-merge'
import { LoginForm } from '@/features/public/auth/components/forms/login-form'

export function LoginView({ className, ...rest }: ComponentProps<'div'>) {
    return (
        <div
            className={twMerge('w-screen h-screen flex justify-center items-center', className)}
            {...rest}
        >
            <LoginForm />
        </div>
    )
}
```

No styling in the view itself — card styling lives in `LoginForm` (the client boundary). The view stays SSR and stays thin, matching the existing pattern.

- [ ] **Step 2: Commit**

```bash
git add src/features/public/auth/views/login-view.tsx
git commit -m "feat: update LoginView — thin wrapper for card-based LoginForm"
```

---

## Task 3: Rewrite LoginForm with Controller + styled card

**Files:**
- Rewrite: `src/features/public/auth/components/forms/login-form/login-form.tsx`

- [ ] **Step 1: Replace login-form.tsx**

```tsx
'use client'

import { useTransition } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { valibotResolver } from '@hookform/resolvers/valibot'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { LoginSchema } from '@/features/public/auth/schemas/auth.schema'
import type { TypeLoginRequest } from '@/features/public/auth/types/auth.types'
import { authQuery } from '@/features/public/auth/queries/auth.query'
import { extractError } from '@/shared/api/api.error'
import { DASHBOARD_PAGE, PUBLIC_PAGE } from '@/shared/configs/page.config'
import { Button, Input, Logo, PasswordInput, Typography } from '@/shared/components/ui'

type FormData = TypeLoginRequest

export function LoginForm() {
    const router = useRouter()
    const [, startTransition] = useTransition()
    const { mutate, isPending } = useMutation(authQuery.login())

    const { control, handleSubmit, reset } = useForm<FormData>({
        mode: 'onChange',
        resolver: valibotResolver(LoginSchema),
        defaultValues: { email: '', password: '' }
    })

    const submit = (data: FormData) => {
        mutate(data, {
            onSuccess: () => {
                startTransition(() => {
                    reset()
                    toast.success('Добро пожаловать')
                    router.replace(DASHBOARD_PAGE.HOME)
                })
            },
            onError: (error) => {
                toast.error(extractError(error))
            }
        })
    }

    return (
        <div className="bg-[#161616] border border-[#2a2a2a] rounded-[16px] p-9 w-[360px] shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
            <div className="flex justify-center mb-7">
                <Logo size="md" />
            </div>

            <div className="mb-6">
                <Typography variant="h5" className="text-white mb-1">
                    Вход в аккаунт
                </Typography>
                <p className="text-sm text-[#666]">
                    Нет аккаунта?{' '}
                    <Link
                        href={PUBLIC_PAGE.REGISTER}
                        className="text-[var(--color-primary-500)] hover:underline"
                    >
                        Зарегистрируйтесь
                    </Link>
                </p>
            </div>

            <form onSubmit={handleSubmit(submit)} className="flex flex-col gap-3">
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
                            value={field.value ?? ''}
                            onChange={field.onChange}
                            placeholder="Пароль"
                            error={fieldState.error?.message}
                        />
                    )}
                />

                <Button
                    type="submit"
                    isLoading={isPending}
                    className="w-full mt-2"
                >
                    Войти
                </Button>
            </form>
        </div>
    )
}
```

- [ ] **Step 2: Verify the app starts without errors**

```bash
cd frontend && npm run dev
```

Open http://localhost:3000/auth/login — the styled card should appear. Check browser console for errors.

- [ ] **Step 3: Commit**

```bash
git add src/features/public/auth/components/forms/login-form/login-form.tsx
git commit -m "feat: rewrite LoginForm — styled card with Controller-based fields"
```

---

## Task 4: Implement RegisterForm (fix filename typo + implement)

**Files:**
- Create: `src/features/public/auth/components/forms/register-form/register-form.tsx`
- Modify: `src/features/public/auth/components/forms/register-form/index.ts`
- Delete: `src/features/public/auth/components/forms/register-form/regsiter-form.tsx`

- [ ] **Step 1: Create register-form.tsx**

```tsx
'use client'

import { useTransition } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { valibotResolver } from '@hookform/resolvers/valibot'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { RegisterSchema } from '@/features/public/auth/schemas/auth.schema'
import type { TypeRegisterRequest } from '@/features/public/auth/types/auth.types'
import { authQuery } from '@/features/public/auth/queries/auth.query'
import { extractError } from '@/shared/api/api.error'
import { DASHBOARD_PAGE, PUBLIC_PAGE } from '@/shared/configs/page.config'
import { Button, Input, Logo, PasswordInput, Typography } from '@/shared/components/ui'

type FormData = TypeRegisterRequest

export function RegisterForm() {
    const router = useRouter()
    const [, startTransition] = useTransition()
    const { mutate, isPending } = useMutation(authQuery.register())

    const { control, handleSubmit, reset } = useForm<FormData>({
        mode: 'onChange',
        resolver: valibotResolver(RegisterSchema),
        defaultValues: { full_name: '', email: '', password: '' }
    })

    const submit = (data: FormData) => {
        mutate(data, {
            onSuccess: () => {
                startTransition(() => {
                    reset()
                    toast.success('Аккаунт создан')
                    router.replace(DASHBOARD_PAGE.HOME)
                })
            },
            onError: (error) => {
                toast.error(extractError(error))
            }
        })
    }

    return (
        <div className="bg-[#161616] border border-[#2a2a2a] rounded-[16px] p-9 w-[360px] shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
            <div className="flex justify-center mb-7">
                <Logo size="md" />
            </div>

            <div className="mb-6">
                <Typography variant="h5" className="text-white mb-1">
                    Создать аккаунт
                </Typography>
                <p className="text-sm text-[#666]">
                    Уже есть аккаунт?{' '}
                    <Link
                        href={PUBLIC_PAGE.LOGIN}
                        className="text-[var(--color-primary-500)] hover:underline"
                    >
                        Войти
                    </Link>
                </p>
            </div>

            <form onSubmit={handleSubmit(submit)} className="flex flex-col gap-3">
                <Controller
                    name="full_name"
                    control={control}
                    render={({ field, fieldState }) => (
                        <Input
                            {...field}
                            placeholder="Имя"
                            error={fieldState.error?.message}
                        />
                    )}
                />

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
                            value={field.value ?? ''}
                            onChange={field.onChange}
                            placeholder="Пароль"
                            error={fieldState.error?.message}
                        />
                    )}
                />

                <Button
                    type="submit"
                    isLoading={isPending}
                    className="w-full mt-2"
                >
                    Зарегистрироваться
                </Button>
            </form>
        </div>
    )
}
```

- [ ] **Step 2: Update index.ts**

Replace contents of `src/features/public/auth/components/forms/register-form/index.ts`:

```ts
export { RegisterForm } from './register-form'
```

- [ ] **Step 3: Delete old misnamed stub**

```bash
rm src/features/public/auth/components/forms/register-form/regsiter-form.tsx
```

- [ ] **Step 4: Commit**

```bash
git add src/features/public/auth/components/forms/register-form/
git commit -m "feat: implement RegisterForm — Controller-based fields, fix filename typo"
```

---

## Task 5: Implement RegisterView

**Files:**
- Implement: `src/features/public/auth/views/register-view.tsx`

- [ ] **Step 1: Replace register-view.tsx**

```tsx
import type { ComponentProps } from 'react'
import { twMerge } from 'tailwind-merge'
import { RegisterForm } from '@/features/public/auth/components/forms/register-form'

export function RegisterView({ className, ...rest }: ComponentProps<'div'>) {
    return (
        <div
            className={twMerge('w-screen h-screen flex justify-center items-center', className)}
            {...rest}
        >
            <RegisterForm />
        </div>
    )
}
```

- [ ] **Step 2: Verify both pages work**

```bash
cd frontend && npm run dev
```

- Open http://localhost:3000/auth/login — login card renders, fields validate, link to register works
- Open http://localhost:3000/auth/register — register card renders, 3 fields validate, link to login works
- Submit login form with wrong credentials — toast error appears
- Submit login form with empty fields — field-level errors appear under inputs

- [ ] **Step 3: Commit**

```bash
git add src/features/public/auth/views/register-view.tsx
git commit -m "feat: implement RegisterView — full-screen centered card"
```
