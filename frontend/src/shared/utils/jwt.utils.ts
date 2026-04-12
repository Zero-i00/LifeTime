export function decodeJwtPayload(token: string): { exp?: number } | null {
    try {
        const payload = token.split('.')[1]
        if (!payload) return null

        const decoded = Buffer.from(payload, 'base64').toString('utf-8')
        return JSON.parse(decoded)
    } catch {
        return null
    }
}

export function isTokenExpired(token: string): boolean {
    const payload = decodeJwtPayload(token)
    if (!payload?.exp) return true

    return Date.now() >= payload.exp * 1000
}
