import { type NextRequest } from 'next/server'
import { protectedMiddleware } from '@/shared/middleware/protected.middleware'
import { authPageMiddleware } from '@/shared/middleware/auth-page.middleware'

export async function proxy(request: NextRequest) {
    const { pathname } = request.nextUrl

    if (pathname.startsWith('/auth')) {
        return authPageMiddleware(request)
    }

    return protectedMiddleware(request)
}

export const config = {
    matcher: ['/dashboard/:path*', '/admin/:path*', '/auth/:path*']
}
