## Context

The frontend is a Nuxt 4 application using Vue 3 Composition API with `<script setup>`. It consists of 4 pages (Gallery, Upload, Search, Logs), 4 shared components (NavBar, ImageCard, ImagePreview, AppFooter), 1 composable (useTheme), and 1 layout (default.vue). All API calls use raw `fetch()` with `useRuntimeConfig()` for the base URL. Currently there are zero tests and no test infrastructure.

## Goals / Non-Goals

**Goals:**
- Add Vitest + @vue/test-utils + @nuxt/test-utils as dev dependencies
- Configure Vitest with Nuxt compatibility (vitest.config.ts)
- Write unit tests for `useTheme` composable
- Write component tests for NavBar, ImageCard, ImagePreview, AppFooter, and default layout
- Write page integration tests for all 4 pages with mocked API responses
- Add `npm run test` script to package.json

**Non-Goals:**
- End-to-end (E2E) tests with Playwright or Cypress — out of scope for this change
- Snapshot testing — not valuable for this project's current stage
- Test coverage thresholds or CI pipeline configuration — deferred to follow-up
- Modifying any production source code — tests must work against current components as-is

## Decisions

1. **Vitest over Jest**: Vitest is the de-facto standard for Vite/Vue projects, shares Vite config syntax, and has first-class Nuxt support via `@nuxt/test-utils`. Jest would require additional transformers and config.

2. **@nuxt/test-utils for page tests**: This package provides `mountSuspended()` and `renderSuspended()` which properly initialize Nuxt context (runtime config, router, etc.) — essential for testing pages that use `useRuntimeConfig()` and `<NuxtLink>`.

3. **Mock fetch at the module level**: Rather than mocking `useRuntimeConfig`, mock `global.fetch` directly in test setup. This keeps tests simple and avoids needing to mock Nuxt runtime config internals.

4. **Test files co-located in `__tests__/` directories**: Each component/page gets a `__tests__/ComponentName.spec.js` alongside it. This follows Vue community conventions and keeps tests close to source.

5. **No TypeScript for tests**: The source components use plain `<script setup>` without TypeScript. Tests should match the source language for consistency and simplicity.

## Risks / Trade-offs

- **@nuxt/test-utils version compatibility**: Nuxt 4 is early-stage; `@nuxt/test-utils` may have API differences vs Nuxt 3 docs → Pin exact compatible version, test with `nuxi prepare` before writing tests
- **Mock fidelity**: Mocked fetch responses may drift from actual API behavior → Keep mocks in sync when backend API changes; acceptance tests catch real issues
- **DOM environment quirks**: `jsdom` may not fully replicate browser behavior for File API, clipboard, or drag-drop → Skip or stub browser-specific features in unit tests; defer to E2E for those paths
