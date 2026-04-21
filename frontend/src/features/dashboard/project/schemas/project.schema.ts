import * as v from 'valibot'

export const LinkSchemaResponse = v.object({
	id: v.number(),
	url: v.string(),
	project_id: v.number(),
	tag: v.nullable(v.string()),
	change_percentage: v.nullable(v.number()),
	schema: v.nullable(v.string()),
	different: v.nullable(v.string()),
	created_at: v.pipe(v.string(), v.isoTimestamp()),
	updated_at: v.pipe(v.string(), v.isoTimestamp()),
})

export const ProjectSchemaResponse = v.object({
	id: v.number(),
	name: v.string(),
	links: v.array(LinkSchemaResponse),
	created_at: v.pipe(v.string(), v.isoTimestamp()),
	updated_at: v.pipe(v.string(), v.isoTimestamp()),
})
