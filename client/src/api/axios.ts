import { client } from '@/api/generated/client.gen'
import { env } from '@/config/env'
import axios, { AxiosError } from 'axios'

export function configureApiClient() {
    const axiosInstance = axios.create({
        baseURL: env.API_URL,
        withCredentials: true,
    })

    axiosInstance.interceptors.response.use(
        (res) => res,
        (err: AxiosError) => Promise.reject(err)
    )

    client.setConfig({
        axios: axiosInstance,
    })
}
