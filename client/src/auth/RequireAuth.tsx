import { useSession } from '@/auth/session'
import { LoadingComponent } from '@/components/LoadingComponent'
import { type JSX } from 'react'
import { Navigate, useLocation } from 'react-router'

export function RequireAuth({ children }: { children: JSX.Element }) {
    const { loading, authenticated } = useSession()
    const location = useLocation()
    if (loading) return <LoadingComponent />
    if (!authenticated)
        return <Navigate to="/login" replace state={{ from: location }} />
    return children
}
