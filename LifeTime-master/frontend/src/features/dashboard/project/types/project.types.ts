import type { InferInput } from 'valibot'
import type { LinkSchemaResponse, ProjectSchemaResponse } from '../schemas/project.schema'

export type TypeProjectResponse = InferInput<typeof ProjectSchemaResponse>
export type TypeLinkResponse = InferInput<typeof LinkSchemaResponse>
