## Why

Currently the engine is hardcoded to Xception (2048-d) for all feature extraction. Adding CLIP and ResNet50 support enables semantic-level search (CLIP) and a lighter/simpler CNN option (ResNet50), making the tool more versatile for different use cases.

## What Changes

- Introduce a **model registry** supporting Xception, ResNet50, and CLIP (ViT-B/32)
- Each model gets its own FAISS index (different dimensions: 2048 / 2048 / 512)
- **API**: `POST /api/search` accepts `?model=xception|resnet50|clip`; `POST /api/ingest` extracts features for all active models by default
- **CLI**: `search` and `ingest` subcommands gain `--model` flag (default: `xception`)
- **Frontend**: search page has a model dropdown; selected model is sent with the search request
- **BREAKING**: `FeatureVector` table stores `model_name` column; old rows without a model are treated as `xception`. FAISS index files are now per-model (`faiss_xception.index`, `faiss_resnet50.index`, `faiss_clip.index`).
- `VECTOR_DIM`, `IMG_SIZE` move from global config into per-model config

## Capabilities

### New Capabilities

- `multi-model-extraction`: Backend model registry — register models (name, dimension, input size, extract function), per-model FAISS indexes, per-model feature storage in DB, and model-aware ingest/search endpoints
- `model-selection-ui`: Frontend model dropdown on search page; CLI `--model` flag

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- `backend/app/feature_extractor.py` — refactored into a registry; `extract_feature()` becomes model-aware
- `backend/app/config.py` — `VECTOR_DIM`, `IMG_SIZE` removed or made model-specific
- `backend/app/faiss_manager.py` — per-model index management
- `backend/app/models.py` — `FeatureVector` gains `model_name` column
- `backend/app/routers/ingest.py` — extract features for all (or selected) models
- `backend/app/routers/search.py` — accept `model` query parameter
- `backend/app/cli.py` — `--model` flag for both subcommands
- `backend/pyproject.toml` — add `transformers` dependency for CLIP
- `frontend/app/pages/search.vue` — model selector UI
- Existing FAISS indexes and DB rows continue to work (migrated / defaulted to `xception`)
