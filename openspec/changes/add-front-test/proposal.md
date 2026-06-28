## Why

The frontend has zero test coverage despite having 4 pages, 4 shared components, and 4 direct API calls. As the project grows, manual testing becomes brittle and time-consuming. Adding frontend testing ensures the UI and API integration behave correctly across theme toggling, image upload, search, and CRUD operations.

## What Changes

- Install Vitest, @vue/test-utils, @nuxt/test-utils as dev dependencies
- Add `vitest.config.ts` and a `test` script to `package.json`
- Write unit tests for the `useTheme` composable
- Write component tests for `NavBar`, `ImageCard`, `ImagePreview`, `AppFooter` (and the `default` layout)
- Write page-level integration tests for `index.vue` (Gallery), `upload.vue`, `search.vue`, and `logs.vue` using mocked API responses
- Mock `useRuntimeConfig()` and `fetch()` for API-dependent tests
- Achieve baseline coverage for all core UI logic and API interaction paths

## Capabilities

### New Capabilities
- `frontend-unit-tests`: Unit and component tests for composables, shared components, and layout
- `frontend-api-tests`: Integration tests for pages that call backend APIs (Gallery, Upload, Search, Logs)
- `frontend-test-infra`: Test infrastructure including Vitest config, Nuxt test utilities setup, mock helpers, and CI test script

### Modified Capabilities

_(none — no existing specs to modify)_

## Impact

- **Dependencies added**: `vitest`, `@vue/test-utils`, `@nuxt/test-utils`, `unplugin-vue-components` (if needed)
- **Files affected**: `package.json`, new `vitest.config.ts`, new `__tests__/` directories
- **No changes** to existing source components, pages, or API contracts
- Tests run in CI with `npm run test`; no production code modified
