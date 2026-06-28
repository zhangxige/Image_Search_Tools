## Why

The backend has zero tests. Critical ingestion, search, and image management logic has no regression coverage, making refactoring risky and defects easy to miss. Adding a comprehensive test suite ensures the API behaves correctly under normal and edge-case conditions, and gives confidence for future changes.

## What Changes

- Add `pytest`, `httpx`, `pytest-cov` as dev dependencies
- Create unit tests for core modules: `feature_extractor`, `faiss_manager`, `models`, `schemas`
- Create integration tests for all API endpoints (ingest, search, images CRUD, logs)
- Add test fixtures for in-memory SQLite database, test client, and mocked feature extractor
- Add a `conftest.py` with shared fixtures and a test `--cov` target

## Capabilities

### New Capabilities
- `unit-tests`: Unit tests for non-API modules (feature_extractor, faiss_manager, models, schemas)
- `api-tests`: Integration tests for all REST API endpoints
- `test-infra`: Test infrastructure (fixtures, conftest, dev dependencies, CI config)

### Modified Capabilities
- (none)

## Impact

- `backend/pyproject.toml` — add dev dependencies
- `backend/app/` — no production code changes
- `backend/tests/` — new test directory with conftest.py and test modules
- CI pipeline may need a test step (future concern)
