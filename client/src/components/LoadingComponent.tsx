import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'

export function LoadingComponent() {
    return (
        <div className="flex justify-center">
            <Button disabled size="lg">
                <Spinner className="size-6" />
                <span className="text-md">Loading...</span>
            </Button>
        </div>
    )
}
