import { AuthService } from '@/api/generated'
import { useSession } from '@/auth/session'
import { useNavigate } from 'react-router'

export function Dashboard() {
    const { user, refresh } = useSession()
    const navigate = useNavigate()

    const handleLogout = async () => {
        await AuthService.logout()
        await refresh()
        void navigate('/login', { replace: true })
    }

    return (
        <div>
            <h1>Dashboard</h1>
            <p>Welcome {user?.first_name}</p>
            <button
                onClick={() => {
                    void handleLogout()
                }}
            >
                Logout
            </button>
        </div>
    )
}
