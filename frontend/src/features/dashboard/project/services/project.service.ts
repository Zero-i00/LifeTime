import { axiosAuth } from '@/shared/api/interceptors/auth.interceptor'
import type { TypeProjectResponse } from '../types/project.types'

class ProjectService {
	private readonly PREFIX = '/project'

	async list() {
		const response = await axiosAuth.get<TypeProjectResponse[]>(`${this.PREFIX}/`)
		return response.data
	}
}

export const projectService = new ProjectService()
