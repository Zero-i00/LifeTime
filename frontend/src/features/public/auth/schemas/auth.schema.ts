import * as v from 'valibot'
import {EmailSchema, PasswordSchema} from "@/shared/schemas/input.schema";

export const LoginSchema = v.object({
    email: EmailSchema,
    password: PasswordSchema
})

export const RegisterSchema = v.object({
    email: EmailSchema,
    password: PasswordSchema,
    full_name: v.pipe(v.string())
})