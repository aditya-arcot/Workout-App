import * as z from 'zod'

export const EnvSchema = z.object({
    API_URL: z.string(),
})
