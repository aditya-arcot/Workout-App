import { AuthService } from '@/api/generated'
import { useSession } from '@/auth/session'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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

    const handleLogin = async () => {
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
        <div className="flex items-center justify-center">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle className="p-0 text-2xl">Login</CardTitle>
                </CardHeader>
                <CardContent>
                    <form className="space-y-4">
                        <div className="space-y-1">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                value={username}
                                onChange={(e) => {
                                    setUsername(e.target.value)
                                }}
                                required
                            />
                        </div>

                        <div className="space-y-1">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => {
                                    setPassword(e.target.value)
                                }}
                                required
                            />
                        </div>
                    </form>
                </CardContent>
                <CardFooter>
                    <Button
                        className="w-full"
                        disabled={loading}
                        type="button"
                        onClick={() => void handleLogin()}
                    >
                        {loading ? 'Logging in…' : 'Login'}
                    </Button>
                </CardFooter>
            </Card>
        </div>
    )
}
