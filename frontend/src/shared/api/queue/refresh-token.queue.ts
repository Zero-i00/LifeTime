import { authBroadcast } from '@/shared/broadcasts/auth.broadcast'
import type { QueuePromise } from '@/shared/api/queue/queue.types'

class RefreshTokenQueue {
    private refreshPromise: Promise<any> | null = null
    private logoutPromise: Promise<any> | null = null
    private failedQueue: Array<QueuePromise> = []
    private unsubscribeBroadcast: (() => void) | null = null
    private waitingForRemoteRefresh = false

    private readonly LOCK_KEY = 'refresh_token_lock'
    private readonly LOCK_TIMEOUT = 10000

    constructor() {
        this.setupBroadcastListener()
    }

    private setupBroadcastListener(): void {
        if (typeof window === 'undefined') return

        this.unsubscribeBroadcast = authBroadcast.listen(message => {
            switch (message.type) {
                case 'REFRESH_SUCCESS':
                    if (this.waitingForRemoteRefresh) {
                        this.waitingForRemoteRefresh = false
                        this.processSuccess()
                    }
                    break

                case 'REFRESH_ERROR':
                case 'LOGOUT':
                    if (this.waitingForRemoteRefresh) {
                        this.waitingForRemoteRefresh = false
                        this.processError(new Error('Remote refresh failed'))
                    }
                    break
            }
        })
    }

    add<T>(request: () => Promise<T>): Promise<T> {
        return new Promise((resolve, reject) => {
            this.failedQueue.push({ resolve, reject })
        })
            .then(() => request())
            .catch(err => Promise.reject(err))
    }

    private isLockedByOtherTab(): boolean {
        if (typeof window === 'undefined') return false

        try {
            const lockData = localStorage.getItem(this.LOCK_KEY)
            if (!lockData) return false

            const { tabId, timestamp } = JSON.parse(lockData)
            const isExpired = Date.now() - timestamp > this.LOCK_TIMEOUT

            if (isExpired) {
                localStorage.removeItem(this.LOCK_KEY)
                return false
            }

            return tabId !== authBroadcast.tabId
        } catch {
            return false
        }
    }

    private tryAcquireLock(): boolean {
        if (typeof window === 'undefined') return true

        try {
            if (this.isLockedByOtherTab()) return false

            const lockData = JSON.stringify({
                tabId: authBroadcast.tabId,
                timestamp: Date.now()
            })

            localStorage.setItem(this.LOCK_KEY, lockData)

            const currentLock = localStorage.getItem(this.LOCK_KEY)
            if (currentLock) {
                const { tabId } = JSON.parse(currentLock)
                return tabId === authBroadcast.tabId
            }

            return false
        } catch {
            return true
        }
    }

    private releaseLock(): void {
        if (typeof window === 'undefined') return

        try {
            const lockData = localStorage.getItem(this.LOCK_KEY)
            if (lockData) {
                const { tabId } = JSON.parse(lockData)
                if (tabId === authBroadcast.tabId) {
                    localStorage.removeItem(this.LOCK_KEY)
                }
            }
        } catch {
            // ignore
        }
    }

    async startRefresh(refreshRequest: () => Promise<any>): Promise<any> {
        if (this.refreshPromise) return this.refreshPromise

        if (this.isLockedByOtherTab()) {
            this.waitingForRemoteRefresh = true
            return authBroadcast.waitForRemoteRefresh(this.LOCK_TIMEOUT)
        }

        if (!this.tryAcquireLock()) {
            this.waitingForRemoteRefresh = true
            return authBroadcast.waitForRemoteRefresh(this.LOCK_TIMEOUT)
        }

        this.refreshPromise = refreshRequest()
            .then(result => {
                authBroadcast.refreshSuccess()
                return result
            })
            .catch(error => {
                authBroadcast.refreshError()
                throw error
            })
            .finally(() => {
                this.refreshPromise = null
                this.releaseLock()
            })

        return this.refreshPromise
    }

    startLogout(logoutRequest: () => Promise<any>): Promise<any> {
        if (this.logoutPromise) return this.logoutPromise

        this.logoutPromise = logoutRequest().finally(() => {
            this.logoutPromise = null
            this.releaseLock()
        })

        return this.logoutPromise
    }

    isLoggingOut(): boolean {
        return this.logoutPromise !== null
    }

    isRefreshing(): boolean {
        return this.refreshPromise !== null || this.waitingForRemoteRefresh || this.isLockedByOtherTab()
    }

    processSuccess(): void {
        this.failedQueue.forEach(promise => promise.resolve(null))
        this.clearQueue()
    }

    processError(error: any): void {
        this.failedQueue.forEach(promise => promise.reject(error))
        this.clearQueue()
    }

    reset(): void {
        this.refreshPromise = null
        this.logoutPromise = null
        this.waitingForRemoteRefresh = false
        this.releaseLock()
        this.clearQueue()
    }

    clearAll(): void {
        this.processError(new Error('User logged out'))
        this.reset()
    }

    private clearQueue(): void {
        this.failedQueue = []
    }

    destroy(): void {
        this.unsubscribeBroadcast?.()
        this.reset()
    }
}

export const refreshTokenQueue = new RefreshTokenQueue()
