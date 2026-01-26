import { AuthService } from '@/api/generated'
import { useSession } from '@/auth/session'
import { Feedback } from '@/components/Feedback'
import { Button } from '@/components/ui/button'
import { NavItem } from '@/lib/nav'
import { notify } from '@/lib/notify'
import { NavLink, Outlet, useNavigate } from 'react-router'

export function AppLayout() {
    const { refresh } = useSession()
    const navigate = useNavigate()

    const handleLogout = async () => {
        await AuthService.logout()
        // TODO check status
        notify.success('Logged out successfully')
        await refresh()
        void navigate('/login', { replace: true })
    }

    return (
        <div className="flex h-dvh flex-col bg-muted">
            <header className="border-b bg-background">
                <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
                    <div className="flex items-baseline gap-4">
                        <NavLink to="/" className="text-2xl font-bold">
                            RepTrack
                        </NavLink>
                        <nav className="flex items-center gap-4">
                            <NavItem to="/">Dashboard</NavItem>
                            <NavItem to="/docs">Docs</NavItem>
                        </nav>
                    </div>
                    <div className="flex items-center gap-2">
                        <Feedback />
                        <Button
                            variant="destructive"
                            onClick={() => void handleLogout()}
                        >
                            Logout
                        </Button>
                    </div>
                </div>
            </header>
            <main className="flex-1">
                <div className="mx-auto max-w-6xl px-4 py-6">
                    <div className="rounded-lg bg-background p-6 shadow-md">
                        <Outlet />
                    </div>
                </div>
            </main>
        </div>
    )
}
