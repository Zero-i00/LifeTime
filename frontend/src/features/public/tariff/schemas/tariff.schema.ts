import * as v from 'valibot'

export const TariffSchemaResponse = v.object({
    id: v.pipe(v.number()),
    title: v.pipe(v.string()),
    description: v.pipe(v.string()),
    link_limit: v.pipe(v.number()),
    project_limit: v.pipe(v.number()),
    price: v.pipe(v.string(), v.decimal()),
    old_price: v.pipe(v.string(), v.decimal()),
    is_initial: v.pipe(v.boolean()),
    created_at: v.pipe(v.string(), v.isoTimestamp()),
    updated_at: v.pipe(v.string(), v.isoTimestamp())
})
