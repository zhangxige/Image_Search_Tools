## 1. Test Infrastructure Setup

- [x] 1.1 Install vitest, @vue/test-utils, @nuxt/test-utils, jsdom as devDependencies
- [x] 1.2 Create vitest.config.ts with Nuxt compatibility
- [x] 1.3 Add "test" script to package.json (vitest run)
- [x] 1.4 Run nuxi prepare and verify vitest discovers tests

## 2. Composable Tests

- [x] 2.1 Write useTheme tests: toggle, localStorage persistence, prefers-color-scheme fallback, data-theme attribute

## 3. Component Tests

- [x] 3.1 Write NavBar tests: nav links, GitHub link from runtime config, theme toggle button
- [x] 3.2 Write ImageCard tests: filename/metadata display, click event emission
- [x] 3.3 Write AppFooter tests: copyright year, project attribution text
- [x] 3.4 Write default layout tests: renders NavBar and AppFooter around slot content

## 4. Page Integration Tests

- [x] 4.1 Create mockFetch helper for stubbing global.fetch with response data
- [x] 4.2 Write Gallery page tests: load images, pagination, tag filter, select-all, batch delete, empty state
- [x] 4.3 Write Upload page tests: file submission with tags, success results display
- [x] 4.4 Write Search page tests: disabled button when empty, search request with top-K, result display
- [x] 4.5 Write Logs page tests: load logs on mount, load-more pagination

## 5. Final Verification

- [x] 5.1 Run full test suite and confirm all tests pass
- [x] 5.2 Verify frontend dev server still works (npm run dev)
