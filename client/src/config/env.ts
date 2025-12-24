import { EnvSchema } from '@/models/env'

const createEnv = () => {
    const env = Object.entries(import.meta.env).reduce<Record<string, string>>(
        (acc, curr: [string, string]) => {
            const [key, value] = curr
            if (key.startsWith('VITE_')) {
                acc[key.replace('VITE_', '')] = value
            }
            return acc
        },
        {}
    )
    const parsedEnv = EnvSchema.safeParse(env)
    if (!parsedEnv.success) throw Error('Failed to parse env vars')
    return parsedEnv.data
}

export const env = createEnv()
