import { useSession } from '@/auth/session'
import { LoadingComponent } from '@/components/LoadingComponent'
import type { JSX } from 'react'
import { Navigate } from 'react-router'

export function RequireGuest({ children }: { children: JSX.Element }) {
    const { loading, authenticated } = useSession()
    if (loading) return <LoadingComponent />
    if (authenticated) return <Navigate to="/" replace />
    return children
}
