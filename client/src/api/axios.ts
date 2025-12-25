import { client, type CreateClientConfig } from '@/api/generated/client.gen'
import { env } from '@/config/env'
import { AxiosError } from 'axios'

export const createClientConfig: CreateClientConfig = (config) => ({
    ...config,
    baseURL: env.API_URL,
    withCredentials: true,
})

client.instance.interceptors.response.use(
    (res) => res,
    (err: AxiosError) => {
        if (err.response?.status === 401) window.location.href = '/login'
        return Promise.reject(err)
    }
)
