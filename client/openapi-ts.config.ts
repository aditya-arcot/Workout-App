import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
    input: 'openapi_spec.json',
    output: 'src/api/generated',
    plugins: [
        '@hey-api/client-axios',
        'zod',
        {
            name: '@hey-api/sdk',
            operations: {
                strategy: 'byTags',
                nesting: 'operationId',
                containerName: '{{name}}Service',
            },
        },
        {
            name: '@hey-api/schemas',
            type: 'json',
        },
    ],
})
