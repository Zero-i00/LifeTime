import { type NextRequest, NextResponse } from 'next/server'
import { DASHBOARD_PAGE } from '@/shared/configs/page.config'
import { isTokenExpired } from '@/shared/utils/jwt.utils'

export function authPageMiddleware(request: NextRequest): NextResponse {
    const accessToken = request.cookies.get('access_token')?.value

    if (accessToken && !isTokenExpired(accessToken)) {
        return NextResponse.redirect(new URL(DASHBOARD_PAGE.HOME, request.url))
    }

    return NextResponse.next()
}
