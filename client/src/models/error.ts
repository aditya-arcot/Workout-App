import type { ErrorResponse } from '@/api/generated'

type HttpErrorHandler = (error: ErrorResponse) => void | Promise<void>

export interface ApiErrorOptions {
    httpErrorHandlers?: Record<string, HttpErrorHandler>
    fallbackMessage: string
}
