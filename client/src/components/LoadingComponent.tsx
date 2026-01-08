import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'

export function LoadingComponent() {
    return (
        <div className="flex min-h-screen items-center justify-center">
            <Button disabled size="lg">
                <Spinner className="size-8" />
                <span className="text-md">Loading...</span>
            </Button>
        </div>
    )
}
