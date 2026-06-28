## ADDED Requirements

### Requirement: Vitest configuration
The project SHALL have a working Vitest configuration compatible with Nuxt 4.

#### Scenario: Vitest runs successfully
- **WHEN** `vitest run` is executed
- **THEN** it SHALL discover and execute all test files without configuration errors

#### Scenario: Nuxt test utilities available
- **WHEN** `@nuxt/test-utils` is imported in a test
- **THEN** `mountSuspended` and `renderSuspended` SHALL be available

### Requirement: Test scripts in package.json
The package.json SHALL have a `test` script that runs Vitest.

#### Scenario: npm run test works
- **WHEN** `npm run test` is executed
- **THEN** Vitest SHALL run and exit with a non-zero code if any test fails

### Requirement: fetch mock helper
The test infrastructure SHALL provide a reusable `mockFetch` helper that stubs `global.fetch`.

#### Scenario: mockFetch returns expected data
- **WHEN** a test uses `mockFetch` to stub GET /api/images
- **THEN** the component SHALL receive and render the mocked data
