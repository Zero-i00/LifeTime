export type QueuePromise = {
    resolve: (value: any) => void
    reject: (reason?: any) => void
}
