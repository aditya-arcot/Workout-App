import type { UserPublic } from '@/api/generated'

export interface SessionContextValue {
    user: UserPublic | null
    loading: boolean
    authenticated: boolean
    refresh: () => Promise<void>
}
