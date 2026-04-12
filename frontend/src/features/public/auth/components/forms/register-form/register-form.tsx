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
        <div className="bg-[#161616] border border-[var(--color-secondary-200)] rounded-[16px] p-9 w-[360px] shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
            <div className="flex justify-center mb-7">
                <Logo size="md" />
            </div>

            <div className="mb-6">
                <Typography variant="h5" className="text-white mb-1">
                    Создать аккаунт
                </Typography>
                <p className="text-sm text-[var(--color-secondary-700)]">
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
                            onBlur={field.onBlur}
                            ref={field.ref}
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
