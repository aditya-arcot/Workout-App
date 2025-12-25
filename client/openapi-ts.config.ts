import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
    input: 'openapi_spec.json',
    output: 'src/api/generated',
    plugins: [
        '@hey-api/client-axios',
        {
            name: '@hey-api/sdk',
            asClass: true,
            operationId: true,
            classNameBuilder: '{{name}}Service',
        },
        {
            name: '@hey-api/schemas',
            type: 'json',
        },
    ],
})
