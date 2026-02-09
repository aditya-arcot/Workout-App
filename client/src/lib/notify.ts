import { logger } from '@/lib/logger'
// eslint-disable-next-line no-restricted-imports
import { toast } from 'sonner'

export const notify = {
    success: (msg: string) => {
        logger.debug('Success notification:', msg)
        toast.success(msg)
    },
    info: (msg: string) => {
        logger.info('Info notification:', msg)
        toast.info(msg)
    },
    warning: (msg: string) => {
        logger.warn('Warning notification:', msg)
        toast.warning(msg)
    },
    error: (msg: string) => {
        logger.error('Error notification:', msg)
        toast.error(msg, {
            duration: 10000,
        })
    },
}
