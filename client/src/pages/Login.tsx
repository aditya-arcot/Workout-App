import { AuthService } from '@/api/generated'
import { zLoginRequest } from '@/api/generated/zod.gen'
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
import { notify } from '@/lib/notify'
import type { LocationState } from '@/models/location'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { Link } from 'react-router-dom'
import { z } from 'zod'

type LoginForm = z.infer<typeof zLoginRequest>

export function Login() {
    const { refresh } = useSession()
    const navigate = useNavigate()

    const location = useLocation()
    const state = location.state as LocationState | null
    const from = state?.from?.pathname ?? '/login'

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        reset,
    } = useForm({
        resolver: zodResolver(zLoginRequest),
        mode: 'onSubmit',
        reValidateMode: 'onChange',
    })

    const onSubmit = async (data: LoginForm) => {
        const res = await AuthService.login({ body: data })
        if (res.status === 401) {
            notify.error('Invalid username or password')
            reset({ password: '' })
            return
        }
        notify.success('Success logging in')
        await refresh()
        void navigate(from, { replace: true })
    }

    return (
        <div className="flex h-dvh items-center justify-center bg-muted px-4">
            <Card className="w-full max-w-sm shadow-md">
                <CardHeader className="-mb-4">
                    <CardTitle className="p-0 text-center text-2xl">
                        Login
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <form
                        id="login-form"
                        className="space-y-4"
                        onSubmit={(e) => {
                            void handleSubmit(onSubmit)(e)
                        }}
                    >
                        <div className="space-y-1">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                autoComplete="username"
                                aria-invalid={!!errors.username}
                                className={
                                    errors.username ? 'border-destructive' : ''
                                }
                                {...register('username')}
                            />
                            {errors.username && (
                                <p className="text-sm text-destructive">
                                    {errors.username.message}
                                </p>
                            )}
                        </div>
                        <div className="space-y-1">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                autoComplete="current-password"
                                aria-invalid={!!errors.password}
                                className={
                                    errors.password ? 'border-destructive' : ''
                                }
                                {...register('password')}
                            />
                            {errors.password && (
                                <p className="text-sm text-destructive">
                                    {errors.password.message}
                                </p>
                            )}
                        </div>
                    </form>
                </CardContent>
                <CardFooter className="flex flex-col gap-3">
                    <Button
                        form="login-form"
                        className="w-full"
                        disabled={isSubmitting}
                        type="submit"
                    >
                        {isSubmitting ? 'Logging in…' : 'Login'}
                    </Button>
                    <div className="text-sm text-muted-foreground">
                        Don&apos;t have an account?{' '}
                        <Link to="/request-access">
                            <Button
                                variant="link"
                                className="p-0 align-baseline"
                            >
                                Request Access
                            </Button>
                        </Link>
                    </div>
                </CardFooter>
            </Card>
        </div>
    )
}
