import {PUBLIC_QUERY_KEY} from "@/shared/configs/query.config";
import type {UseMutationOptions} from "@tanstack/react-query";
import type {AuthResponse, TypeLoginRequest, TypeRegisterRequest} from "@/features/public/auth/types/auth.types";
import {authService} from "@/features/public/auth/services/auth.service";
import {tokenService} from "@/shared/services/token.service";
import {authBroadcast} from "@/shared/broadcasts/auth.broadcast";
import {refreshTokenQueue} from "@/shared/api/queue/refresh-token.queue";


class AuthQuery {
    public readonly BASE_KEY = [PUBLIC_QUERY_KEY, 'auth']

    login(): UseMutationOptions<AuthResponse, Error, TypeLoginRequest> {
        return {
            mutationKey: [...this.BASE_KEY, 'login'],
            mutationFn: data => authService.login(data),
            onSuccess: data => {
                tokenService.save(data.access_token)
            }
        }
    }

    register(): UseMutationOptions<AuthResponse, Error, TypeRegisterRequest> {
        return {
            mutationKey: [...this.BASE_KEY, 'register'],
            mutationFn: data => authService.register(data),
            onSuccess: data => {
                tokenService.save(data.access_token)
            }
        }
    }

    logout(): UseMutationOptions<boolean, Error, undefined> {
        return {
            mutationKey: [...this.BASE_KEY, 'logout'],
            mutationFn: () => authService.logout(),
            onSuccess: () => {
                tokenService.remove()
                authBroadcast.logout()
                refreshTokenQueue.clearAll()
            }
        }
    }
}

export const authQuery = new AuthQuery()
