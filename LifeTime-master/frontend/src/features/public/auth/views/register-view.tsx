import type { ComponentProps } from 'react'
import { twMerge } from 'tailwind-merge'
import { RegisterForm } from '@/features/public/auth/components/forms/register-form'

export function RegisterView({ className, ...rest }: ComponentProps<'div'>) {
    return (
        <div
            className={twMerge('w-full min-h-screen flex justify-center items-center', className)}
            {...rest}
        >
            <RegisterForm />
        </div>
    )
}