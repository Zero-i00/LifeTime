import { queryOptions, type UseMutationOptions } from '@tanstack/react-query'
import { DASHBOARD_QUERY_KEY } from '@/shared/configs/query.config'
import type { TypeUserResponse } from '@/features/public/user/types/user.types'
import type { TypeUserProfileUpdate } from '../types/user.types'
import { userService } from '../services/user.service'

class UserQuery {
	public readonly BASE_KEY = [DASHBOARD_QUERY_KEY, 'user']

	profile() {
		return queryOptions({
			queryKey: [...this.BASE_KEY, 'profile'],
			queryFn: () => userService.getProfile(),
		})
	}

	updateProfile(): UseMutationOptions<TypeUserResponse, Error, TypeUserProfileUpdate> {
		return {
			mutationKey: [...this.BASE_KEY, 'profile', 'update'],
			mutationFn: (data) => userService.updateProfile(data),
		}
	}
}

export const userQuery = new UserQuery()
