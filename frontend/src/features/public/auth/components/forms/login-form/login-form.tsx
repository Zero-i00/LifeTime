'use client'

import {type ComponentProps, useTransition} from "react";
import {LoginSchema} from "@/features/public/auth/schemas/auth.schema";
import type {TypeLoginRequest} from "@/features/public/auth/types/auth.types";
import {useForm} from "react-hook-form";
import {valibotResolver} from "@hookform/resolvers/valibot";
import {useMutation} from "@tanstack/react-query";
import {authQuery} from "@/features/public/auth/queries/auth.query";
import toast from "react-hot-toast";
import {extractError} from "@/shared/api/api.error";
import {useRouter} from "next/navigation";
import {DASHBOARD_PAGE} from "@/shared/configs/page.config";
import {twMerge} from "tailwind-merge";

const FormSchema = LoginSchema
type FormData = TypeLoginRequest

export function LoginForm({className, ...rest}: ComponentProps<'form'>) {

    const router = useRouter()

    const [isMouting, startTransition] = useTransition()
    const {mutate, isPending} = useMutation(authQuery.login())

    const {
        reset,
        register,
        handleSubmit,
    } = useForm<FormData>({
        mode: 'onChange',
        resolver: valibotResolver(FormSchema)
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
        <form className={twMerge(`flex flex-col gap-4 bg-gray-100`, className)} {...rest}>
            <input {...register('email')} required className={`border`} type="text" placeholder={'email'}/>
            <input {...register('password')} required className={`border`} type="password" placeholder={'password'}/>
            <button type={'submit'} onClick={handleSubmit(submit)}>
                Войти
            </button>
        </form>
    )
}