import { axiosAuth } from '@/shared/api/interceptors/auth.interceptor'
import type { TypeUserResponse } from '@/features/public/user/types/user.types'
import type { TypeUserProfileUpdate } from '../types/user.types'

class UserService {
	private readonly PREFIX = '/user'

	async getProfile() {
		const response = await axiosAuth.get<TypeUserResponse>(`${this.PREFIX}/profile`)
		return response.data
	}

	async updateProfile(data: TypeUserProfileUpdate) {
		const response = await axiosAuth.patch<TypeUserResponse>(`${this.PREFIX}/profile`, data)
		return response.data
	}
}

export const userService = new UserService()
