import { AuthService } from '@/api/generated'
import { useSession } from '@/auth/session'
import type { LocationState } from '@/models/location'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

export function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const location = useLocation()
    const state = location.state as LocationState | null
    const from = state?.from?.pathname ?? '/login'

    const { refresh } = useSession()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            await AuthService.login({ body: { username, password } })
            await refresh()
            void navigate(from, { replace: true })
        } finally {
            setLoading(false)
        }
    }

    return (
        <form
            onSubmit={(e) => {
                void handleSubmit(e)
            }}
        >
            <h1>Login</h1>
            <input
                type="text"
                value={username}
                onChange={(e) => {
                    setUsername(e.target.value)
                }}
                placeholder="Username"
                required
            />
            <br />
            <input
                type="password"
                value={password}
                onChange={(e) => {
                    setPassword(e.target.value)
                }}
                placeholder="Password"
                required
            />
            <br />
            <button disabled={loading} type="submit">
                {loading ? 'Logging in…' : 'Login'}
            </button>
        </form>
    )
}
