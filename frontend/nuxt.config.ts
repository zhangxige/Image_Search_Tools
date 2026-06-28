export default defineNuxtConfig({
  compatibilityDate: '2026-01-01',
  future: {
    compatibilityVersion: 4,
  },
  devtools: { enabled: true },
  srcDir: 'app/',
  css: ['~/assets/main.css'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      githubRepo: process.env.NUXT_PUBLIC_GITHUB_REPO || '',
    },
  },
  app: {
    head: {
      title: 'Image Search Engine',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
})
