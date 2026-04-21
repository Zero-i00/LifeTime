import type { InferInput } from 'valibot'
import type { UserProfileUpdateSchema } from '../schemas/user.schema'

export type TypeUserProfileUpdate = InferInput<typeof UserProfileUpdateSchema>
