import type {InferInput} from 'valibot'
import {UserSchemaResponse} from "@/features/public/user/schemas/user.schema";

export const UserRoleEnum = {
    ADMIN: 'ADMIN',
    USER: 'USER'
} as const

export type UserRoleEnum = (typeof UserRoleEnum)[keyof typeof UserRoleEnum]

export type TypeUserResponse = InferInput<typeof UserSchemaResponse>
