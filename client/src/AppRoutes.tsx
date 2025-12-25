import { RequireAuth } from '@/auth/RequireAuth'
import { RequireGuest } from '@/auth/RequireGuest'
import { AppLayout } from '@/layout/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Login } from '@/pages/Login'
import { Route, Routes } from 'react-router'

export function AppRoutes() {
    return (
        <Routes>
            <Route
                path="/"
                element={
                    <RequireAuth>
                        <AppLayout />
                    </RequireAuth>
                }
            >
                <Route index element={<Dashboard />} />
            </Route>

            <Route
                path="/login"
                element={
                    <RequireGuest>
                        <Login />
                    </RequireGuest>
                }
            />
        </Routes>
    )
}
