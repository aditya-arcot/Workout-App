import { AuthService, type RefreshTokenData } from '@/api/generated'
import { client } from '@/api/generated/client.gen'
import { env } from '@/config/env'
import axios, { AxiosError } from 'axios'

// created for type safety
const refreshUrl = client.buildUrl<RefreshTokenData>({
    url: '/api/auth/refresh-token',
})

export function configureApiClient() {
    const axiosInstance = axios.create({
        baseURL: env.API_URL,
        withCredentials: true,
    })

    let isRefreshing = false
    let failedQueue: {
        resolve: (value?: unknown) => void
        reject: (error: unknown) => void
    }[] = []

    const processQueue = (error: unknown, tokenUpdated = false) => {
        failedQueue.forEach(({ resolve, reject }) => {
            if (error) reject(error)
            else resolve(tokenUpdated)
        })
        failedQueue = []
    }

    axiosInstance.interceptors.response.use(
        (res) => res,
        async (error: AxiosError) => {
            const originalRequest = error.config
            if (!originalRequest) return Promise.reject(error)

            if (
                error.response?.status === 401 &&
                !originalRequest._retry &&
                !originalRequest.url?.endsWith(refreshUrl)
            ) {
                if (isRefreshing) {
                    // queue requests
                    return new Promise((resolve, reject) => {
                        failedQueue.push({ resolve, reject })
                    }).then(() => axiosInstance(originalRequest))
                }

                originalRequest._retry = true
                isRefreshing = true

                try {
                    await AuthService.refreshToken()
                    processQueue(null, true)
                    return await axiosInstance(originalRequest)
                } catch (err) {
                    processQueue(err, false)
                    throw err
                } finally {
                    isRefreshing = false
                }
            }

            return Promise.reject(error)
        }
    )

    client.setConfig({
        axios: axiosInstance,
    })
}
