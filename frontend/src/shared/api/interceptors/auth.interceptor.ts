import axios, { type CreateAxiosDefaults, type InternalAxiosRequestConfig } from "axios";
import { API_SERVER_URL } from "@/shared/configs/api.config";
import { APP_API_HEADER } from "@/shared/api/api.helper";
import { tokenService } from "@/shared/services/token.service";
import { refreshTokenQueue } from "@/shared/api/queue/refresh-token.queue";
import { axiosClient } from "@/shared/api/interceptors/root.interceptor";
import { PUBLIC_PAGE } from "@/shared/configs/page.config";
import type { AuthResponse } from "@/features/public/auth/types/auth.types";

interface RetryableRequest extends InternalAxiosRequestConfig {
    _isRetry?: boolean
}

const options: CreateAxiosDefaults = {
    baseURL: API_SERVER_URL,
    headers: APP_API_HEADER,
    withCredentials: true
}

export const axiosAuth = axios.create(options)

axiosAuth.interceptors.request.use(config => {
    const token = tokenService.get()

    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    return config
})

axiosAuth.interceptors.response.use(
    response => response,
    async (error) => {
        const originalRequest: RetryableRequest = error.config

        if (error.response?.status !== 401 || originalRequest._isRetry) {
            return Promise.reject(error)
        }

        originalRequest._isRetry = true

        if (refreshTokenQueue.isRefreshing()) {
            return refreshTokenQueue.add(() => axiosAuth(originalRequest))
        }

        try {
            const data = await refreshTokenQueue.startRefresh(() =>
                axiosClient
                    .post<AuthResponse>('/auth/refresh_token')
                    .then(res => res.data)
            )

            tokenService.save(data.access_token)
            refreshTokenQueue.processSuccess()

            return axiosAuth(originalRequest)
        } catch {
            refreshTokenQueue.processError(new Error('Refresh failed'))
            tokenService.remove()

            if (typeof window !== 'undefined') {
                window.location.href = PUBLIC_PAGE.LOGIN
            }

            return Promise.reject(error)
        }
    }
)
