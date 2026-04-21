import type {InferInput} from 'valibot'
import type { LoginSchema, RegisterSchema} from "@/features/public/auth/schemas/auth.schema";
import type {TypeUserResponse} from "@/features/public/user/types/user.types";

export const AuthTokenEnum = {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token'
} as const

export type AuthTokenEnum = (typeof AuthTokenEnum)[keyof typeof AuthTokenEnum]

export const TokenTypeEnum = {
    BEARER: 'Bearer'
} as const

export type TokenTypeEnum = (typeof TokenTypeEnum)[keyof typeof TokenTypeEnum]

export type TypeLoginRequest = InferInput<typeof LoginSchema>

export type TypeRegisterRequest = InferInput<typeof RegisterSchema>

export type AuthResponse = {
    access_token: string
    user: TypeUserResponse,
    token_type: TokenTypeEnum
}
