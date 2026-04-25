export type Link = {
	id: number
	url: string
	project_id: number
	created_at: Date,
	updated_at: Date,
	schema: string,
	different: string,
	tag: string,
	attrs: string
	change_percentage: number
}

export type LinkRequest = {
	url: string
	project_id: number
	type: 'GET' | 'POST'
}

export type LinkResponse = Link[]
