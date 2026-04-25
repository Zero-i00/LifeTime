import { axiosAuth } from '@/shared/api/interceptors/auth.interceptor'
import type { Link, LinkRequest } from '../types/link.types'


class LinkService {
	private BASE_URL = '/links'

	async list() {
		const response = await axiosAuth.get<Link[]>(`${this.BASE_URL}`)

		return response.data
	}

	async retrieve(id: string) {
		const response = await axiosAuth.get<Link>(`${this.BASE_URL}/${id}`)

		return response.data
	}

	async create(meta: LinkRequest) {
		const response = await axiosAuth.post<Link>(`${this.BASE_URL}/`, {
			...meta,
		})

		return response.data
	}

	async update(id: string, meta: LinkRequest) {
		const response = await axiosAuth.patch<Link>(
			`${this.BASE_URL}/${id}/`,
			{
				...meta,
			}
		)

		return response.data
	}

	async destroy(id: string) {
		const response = await axiosAuth.delete(`${this.BASE_URL}/${id}/`)

		return response.data
	}
}

export const linkService = new LinkService()
