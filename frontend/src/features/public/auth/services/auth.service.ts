import type {AuthResponse, TypeLoginRequest, TypeRegisterRequest} from "@/features/public/auth/types/auth.types";
import {axiosClient} from "@/shared/api/interceptors/root.interceptor";


class AuthService {
    private readonly PREFIX = '/auth'

    async login(meta: TypeLoginRequest) {
        const response = await axiosClient.post<AuthResponse>(`${this.PREFIX}/login`, {
            ...meta
        })

        return response.data
    }

    async register(meta: TypeRegisterRequest) {
        const response = await axiosClient.post<AuthResponse>(`${this.PREFIX}/register`, {
            ...meta
        })

        return response.data
    }

    async refresh() {
        const response = await axiosClient.post<AuthResponse>(`${this.PREFIX}/refresh_token`)

        return response.data
    }

    async logout() {
        const response = await axiosClient.post<boolean>(`${this.PREFIX}/logout`)

        return response.data
    }
}

export const authService = new AuthService()
