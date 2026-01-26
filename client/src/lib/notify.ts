// eslint-disable-next-line no-restricted-imports
import { toast } from 'sonner'

export const notify = {
    success: (msg: string) => toast.success(msg),
    info: (msg: string) => toast.info(msg),
    warning: (msg: string) => toast.warning(msg),
    error: (msg: string) =>
        toast.error(msg, {
            duration: 10000,
        }),
}
