import { type NextRequest, NextResponse } from 'next/server'
import { PUBLIC_PAGE } from '@/shared/configs/page.config'
import { SERVER_URL } from '@/shared/configs/api.config'
import { isTokenExpired } from '@/shared/utils/jwt.utils'

export async function protectedMiddleware(request: NextRequest): Promise<NextResponse> {
    const accessToken = request.cookies.get('access_token')?.value

    if (!accessToken) {
        return NextResponse.redirect(new URL(PUBLIC_PAGE.LOGIN, request.url))
    }

    if (!isTokenExpired(accessToken)) {
        return NextResponse.next()
    }

    try {
        const refreshResponse = await fetch(`${SERVER_URL}/api/v1/auth/refresh_token`, {
            method: 'POST',
            headers: {
                Cookie: request.headers.get('cookie') ?? ''
            },
            credentials: 'include'
        })

        if (!refreshResponse.ok) {
            return NextResponse.redirect(new URL(PUBLIC_PAGE.LOGIN, request.url))
        }

        const data = await refreshResponse.json()
        const newToken: string = data.access_token

        const response = NextResponse.next()
        response.cookies.set('access_token', newToken, {
            httpOnly: false,
            maxAge: 15 * 60,
            path: '/',
            sameSite: 'strict'
        })

        return response
    } catch {
        return NextResponse.redirect(new URL(PUBLIC_PAGE.LOGIN, request.url))
    }
}
