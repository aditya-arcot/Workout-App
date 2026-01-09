import type { UserPublic } from '@/api/generated'

export interface SessionContextType {
    user: UserPublic | null
    loading: boolean
    authenticated: boolean
    refresh: () => Promise<void>
}
