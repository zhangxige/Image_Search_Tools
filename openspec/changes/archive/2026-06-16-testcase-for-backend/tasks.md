## 1. Test Infrastructure

- [x] 1.1 Add `pytest`, `httpx`, `pytest-cov` to `pyproject.toml` dev dependencies
- [x] 1.2 Create `backend/tests/` directory with `__init__.py`
- [x] 1.3 Create `backend/tests/conftest.py` with shared fixtures: `db_session`, `client`, `mock_feature_extractor`, `sample_image`, `sample_image_file`

## 2. Unit Tests

- [x] 2.1 Create `tests/test_models.py` — test ORM mapping, relationships, cascade delete, binary vector round-trip
- [x] 2.2 Create `tests/test_schemas.py` — test Pydantic validation, serialization, partial updates
- [x] 2.3 Create `tests/test_faiss_manager.py` — test build_index, add_to_index, search, rebuild_from_db
- [x] 2.4 Create `tests/test_feature_extractor.py` — test extract_feature from PIL Image and file path, error handling

## 3. API Integration Tests

- [x] 3.1 Create `tests/test_ingest.py` — test single/batch ingestion, tags, invalid file handling
- [x] 3.2 Create `tests/test_search.py` — test search with/without results, top_k, invalid file
- [x] 3.3 Create `tests/test_images.py` — test list (pagination + tag filter), count, single delete, batch delete, 404, update, logs
