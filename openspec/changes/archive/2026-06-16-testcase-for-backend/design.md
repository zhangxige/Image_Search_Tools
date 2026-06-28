## Context

The backend is a FastAPI application with SQLAlchemy + SQLite, FAISS vector search, and a PyTorch/timm Xception feature extractor. All API endpoints are synchronous. There is no existing test infrastructure. The heavy ML dependency (PyTorch + timm) makes loading the real model in tests impractical — mocking is required.

## Goals / Non-Goals

**Goals:**
- Unit test coverage for `models.py`, `schemas.py`, `faiss_manager.py`, `feature_extractor.py`
- Integration test coverage for all 6 API endpoints (ingest, search, list, count, delete, update, logs)
- Shared test fixtures: in-memory SQLite DB, `TestClient`, mocked feature extractor
- Dev dependencies: `pytest`, `httpx`, `pytest-cov`

**Non-Goals:**
- End-to-end tests requiring a running server or GPU
- Performance / load tests
- Frontend tests
- CI pipeline configuration (beyond the test command)

## Decisions

1. **pytest + httpx over unittest** — pytest is the de-facto Python test framework. `httpx` provides the `AsyncClient`-compatible `TestClient` for FastAPI, but since endpoints are synchronous, Starlette's built-in `TestClient` is sufficient. This avoids unnecessary async complexity.

2. **In-memory SQLite for test DB** — Replace the `DATABASE_URL` with `sqlite:///:memory:` in fixtures. Fast, isolated, and requires no cleanup. Each test function gets a fresh connection via `override_get_db`.

3. **Mock `extract_feature` at the router level** — The heaviest dependency is the Xception model. Instead of loading it, mock `app.feature_extractor.extract_feature` to return a random 2048-d L2-normalized vector. This keeps tests fast while still exercising the search/ingest pipeline logic.

4. **FAISS in-memory for tests** — FAISS works with numpy arrays directly. Tests can build a small index from scratch without persisting to disk. The `faiss_manager.build_index()` is fine as-is since it accepts a dimension parameter.

5. **Fixtures in `conftest.py`** — Shared fixtures (db session, test client, mock feature extractor, sample image buffer) in `conftest.py` at the `tests/` root. Module-specific fixtures stay in individual test files.

## Risks / Trade-offs

- **Mocked features != real features** — The mock returns random vectors, so similarity scores are meaningless. This is acceptable because tests verify API behavior (status codes, response structure, DB writes), not feature accuracy.
- **SQLite vs PostgreSQL in production** — SQLite dialect differences are minimal for the simple queries used. If the app ever migrates to PostgreSQL, the ORM abstraction should handle it, but some SQLAlchemy dialect-specific behavior may differ.
- **FAISS index rebuild on delete** — `rebuild_from_db()` queries the DB and rebuilds the entire index. Tests that exercise delete must ensure the DB has known state. Fixtures with pre-seeded images handle this.
