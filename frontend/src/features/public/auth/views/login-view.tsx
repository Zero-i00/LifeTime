import type {ComponentProps} from "react";
import {twMerge} from "tailwind-merge";
import {LoginForm} from "@/features/public/auth/components/forms/login-form";

export function LoginView({className, ...rest}: ComponentProps<'div'>) {
    return (
        <div className={twMerge(`w-screen h-screen flex justify-center items-center`, className)} {...rest}>
            <LoginForm />
        </div>
    )
}