import type { ErrorResponse, HttpValidationError } from '@/api/generated'

export function isHttpError(error: unknown): error is ErrorResponse {
    return (
        typeof error === 'object' &&
        error !== null &&
        'code' in error &&
        typeof error.code === 'string' &&
        'detail' in error &&
        typeof error.detail === 'string'
    )
}

export function isHttpValidationError(
    error: unknown
): error is HttpValidationError {
    return (
        typeof error === 'object' &&
        error !== null &&
        'detail' in error &&
        Array.isArray(error.detail)
    )
}
