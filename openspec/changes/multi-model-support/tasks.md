## 1. Backend: Model Registry

- [x] 1.1 Add `transformers` dependency to `pyproject.toml`
- [x] 1.2 Refactor `feature_extractor.py` into a model registry with lazy-loaded `xception`, `resnet50`, `clip` entries — each exposing `name`, `dim`, `input_size`, `load_fn()`, and `extract(image) -> np.ndarray`
- [x] 1.3 Keep existing `extract_feature()` and `extract_feature_from_path()` as aliases for the default model (`xception`) for backward compat
- [x] 1.4 Thread-safe lazy loading with `threading.Lock` per model

## 2. Backend: Per-Model FAISS Manager

- [x] 2.1 Refactor `faiss_manager.py` to manage per-model indexes: `faiss_xception.index`, `faiss_resnet50.index`, `faiss_clip.index` (with separate `_id_to_index`/`_index_to_id` mappings and locks)
- [x] 2.2 Update `add_to_index()` to accept `model_name` parameter
- [x] 2.3 Update `search()` to accept `model_name` parameter
- [x] 2.4 Update `rebuild_from_db()` to filter by `model_name` and rebuild only that model's index
- [x] 2.5 Handle legacy `faiss.index` → `faiss_xception.index` rename on startup
- [x] 2.6 Update `save_index()` / `load_index()` to be model-aware

## 3. Backend: Database Migration

- [x] 3.1 Add `model_name` column (`String(50)`, NOT NULL, default `"xception"`) to `FeatureVector` model
- [x] 3.2 Add unique constraint on `(image_id, model_name)` to `FeatureVector`
- [x] 3.3 Create migration logic: `ALTER TABLE feature_vectors ADD COLUMN model_name VARCHAR(50) NOT NULL DEFAULT 'xception'`

## 4. Backend: API Endpoints

- [x] 4.1 Add `GET /api/models` returning `["xception", "resnet50", "clip"]`
- [x] 4.2 Update `POST /api/ingest` to accept optional `model` query param — without param, extract for all models; with param, extract only for that model
- [x] 4.3 Update `POST /api/search` to accept `model` query param (default `"xception"`) and route to the correct FAISS index
- [x] 4.4 Include `model` field in search response

## 5. Backend: CLI

- [x] 5.1 Add `--model` option to `ingest` subcommand (choices: `xception`, `resnet50`, `clip`; default: ingest for all models)
- [x] 5.2 Add `--model` option to `search` subcommand (choices: `xception`, `resnet50`, `clip`; default: `xception`)
- [x] 5.3 Pass `model` parameter in httpx POST requests

## 6. Frontend: Model Selector

- [x] 6.1 Fetch `GET /api/models` on search page load to populate dropdown
- [x] 6.2 Add model dropdown UI to search page (positioned near Top-K input)
- [x] 6.3 Pass selected model as `model` field in search FormData
- [x] 6.4 Display used model name in search results

## 7. Tests

- [x] 7.1 Write pytest tests for model registry (registration, lazy loading, unknown model error)
- [x] 7.2 Write pytest tests for per-model FAISS index (separate indexes, rebuild filtering)
- [x] 7.3 Write pytest tests for model-aware ingest (all models, specific model)
- [x] 7.4 Write pytest tests for model-aware search (model param, default, unknown model)
- [x] 7.5 Write pytest tests for `GET /api/models` endpoint
- [x] 7.6 Write pytest tests for CLI `--model` flags
- [x] 7.7 Write Vitest tests for frontend model selector (dropdown population, model param in request)
- [x] 7.8 Verify existing tests still pass with backward-compatible changes (run `uv sync && uv run pytest tests/` from Windows native terminal)
