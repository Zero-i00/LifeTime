import { IS_CLIENT } from '@/shared/constants/root.constants'
import { generateUuid } from '@/shared/utils/generate-uuid'

type AuthBroadcastMessageType = 'LOGOUT' | 'REFRESH_SUCCESS' | 'REFRESH_ERROR'

interface AuthBroadcastMessage {
    tabId: string
    timestamp: number
    type: AuthBroadcastMessageType
}

type AuthBroadcastCallback = (message: AuthBroadcastMessage) => void

const CHANNEL_NAME = 'auth_broadcast_channel'

class AuthBroadcast {
    readonly tabId = generateUuid()
    private readonly channel?: BroadcastChannel

    constructor() {
        if (IS_CLIENT && 'BroadcastChannel' in window) {
            this.channel = new BroadcastChannel(CHANNEL_NAME)
        }
    }

    send(type: AuthBroadcastMessageType): void {
        if (!this.channel) return

        this.channel.postMessage({
            type,
            tabId: this.tabId,
            timestamp: Date.now()
        } satisfies AuthBroadcastMessage)
    }

    logout(): void {
        this.send('LOGOUT')
    }

    refreshSuccess(): void {
        this.send('REFRESH_SUCCESS')
    }

    refreshError(): void {
        this.send('REFRESH_ERROR')
    }

    listen(callback: AuthBroadcastCallback): () => void {
        if (!this.channel) return () => {}

        const handler = (event: MessageEvent<AuthBroadcastMessage>) => {
            const message = event.data

            if (!message?.type) return
            if (message.tabId === this.tabId) return

            callback(message)
        }

        this.channel.addEventListener('message', handler)

        return () => {
            this.channel?.removeEventListener('message', handler)
        }
    }

    waitForRemoteRefresh(timeout = 10000): Promise<void> {
        if (!this.channel) return Promise.resolve()

        return new Promise((resolve, reject) => {
            const unsubscribe = this.listen(message => {
                if (message.type === 'REFRESH_SUCCESS') {
                    cleanup()
                    resolve()
                }

                if (message.type === 'REFRESH_ERROR' || message.type === 'LOGOUT') {
                    cleanup()
                    reject(new Error('Remote refresh failed'))
                }
            })

            const timer = setTimeout(() => {
                cleanup()
                resolve()
            }, timeout)

            function cleanup() {
                clearTimeout(timer)
                unsubscribe()
            }
        })
    }

    destroy(): void {
        this.channel?.close()
    }
}

export const authBroadcast = new AuthBroadcast()
