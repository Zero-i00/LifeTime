import {PUBLIC_QUERY_KEY} from "@/shared/configs/query.config";
import type {UseMutationOptions} from "@tanstack/react-query";
import type {AuthResponse, TypeLoginRequest, TypeRegisterRequest} from "@/features/public/auth/types/auth.types";
import {authService} from "@/features/public/auth/services/auth.service";


class AuthQuery {
    public readonly BASE_KEY = [PUBLIC_QUERY_KEY, 'auth']

    login(): UseMutationOptions<AuthResponse, Error, TypeLoginRequest> {
        return {
            mutationKey: [...this.BASE_KEY, 'login'],
            mutationFn: data => authService.login(data),
        }
    }

    register(): UseMutationOptions<AuthResponse, Error, TypeRegisterRequest> {
        return {
            mutationKey: [...this.BASE_KEY, 'register'],
            mutationFn: data => authService.register(data),
        }
    }

    logout(): UseMutationOptions<boolean, Error, undefined> {
        return {
            mutationKey: [...this.BASE_KEY, 'logout'],
            mutationFn: () => authService.logout()
        }
    }
}

export const authQuery = new AuthQuery()
