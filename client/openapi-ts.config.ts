import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
    input: 'openapi_spec.json',
    output: 'src/api',
})
