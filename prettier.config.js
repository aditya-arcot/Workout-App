module.exports = {
    trailingComma: 'es5',
    semi: false,
    singleQuote: true,
    plugins: [
        'prettier-plugin-organize-imports',
        'prettier-plugin-toml',
        // must be last
        'prettier-plugin-tailwindcss',
    ],
    tailwindStylesheet: './client/src/index.css',
}
