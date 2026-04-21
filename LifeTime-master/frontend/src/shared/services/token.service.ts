import Cookies from 'js-cookie'

const COOKIE_NAME = 'access_token'
const COOKIE_EXPIRES = 1 / 96 // 15 минут

class TokenService {
    save(token: string): void {
        Cookies.set(COOKIE_NAME, token, { expires: COOKIE_EXPIRES })
    }

    get(): string | undefined {
        return Cookies.get(COOKIE_NAME)
    }

    remove(): void {
        Cookies.remove(COOKIE_NAME)
    }
}

export const tokenService = new TokenService()
