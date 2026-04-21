import * as v from 'valibot'
import { EmailSchema } from '@/shared/schemas/input.schema'

export const UserProfileUpdateSchema = v.object({
	full_name: v.pipe(v.string(), v.minLength(1, 'Имя обязательно')),
	email: EmailSchema,
})
