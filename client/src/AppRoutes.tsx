import { RequireAuth } from '@/auth/RequireAuth'
import { RequireGuest } from '@/auth/RequireGuest'
import { Doc } from '@/components/Doc'
import { DocsIndex } from '@/components/DocsIndex'
import { AppLayout } from '@/layout/AppLayout'
import { Admin } from '@/pages/Admin'
import { Dashboard } from '@/pages/Dashboard'
import { Docs } from '@/pages/Docs'
import { Login } from '@/pages/Login'
import { RequestAccess } from '@/pages/RequestAccess'
import { Navigate, Route, Routes } from 'react-router'

export function AppRoutes() {
    return (
        <Routes>
            <Route
                path="/"
                element={
                    <RequireAuth requireAdmin={false}>
                        <AppLayout />
                    </RequireAuth>
                }
            >
                <Route index element={<Dashboard />} />
                <Route path="docs" element={<Docs />}>
                    <Route index element={<DocsIndex />} />
                    <Route path=":slug" element={<Doc />} />
                </Route>
                <Route
                    path="admin"
                    element={
                        <RequireAuth requireAdmin={true}>
                            <Admin />
                        </RequireAuth>
                    }
                />
            </Route>
            <Route
                path="/request-access"
                element={
                    <RequireGuest>
                        <RequestAccess />
                    </RequireGuest>
                }
            />
            <Route
                path="/login"
                element={
                    <RequireGuest>
                        <Login />
                    </RequireGuest>
                }
            />
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    )
}
