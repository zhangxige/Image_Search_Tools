## ADDED Requirements

### Requirement: Model Registry

The system SHALL maintain a registry of feature extraction models. Each model entry MUST include a unique name, feature dimension, input image size, a lazy loader function, and a preprocessing transform.

- Registered models: `xception`, `resnet50`, `clip`
- `xception` MUST use timm `xception` (2048-d, 299×299 input)
- `resnet50` MUST use timm `resnet50` (2048-d, 224×224 input)
- `clip` MUST use `transformers` `openai/clip-vit-base-patch32` (512-d, 224×224 input)
- All models SHALL output L2-normalized float32 vectors
- Models SHALL be loaded lazily on first use (not at import time)
- Model loading MUST be thread-safe

#### Scenario: Registry lists all registered models
- **WHEN** the system calls the registry for available models
- **THEN** it MUST return at least `["xception", "resnet50", "clip"]`

#### Scenario: Lazy loading does not block import
- **WHEN** the module is imported
- **THEN** no model weights SHALL be loaded into memory until explicitly requested

#### Scenario: Unknown model raises error
- **WHEN** a request specifies a model name not in the registry
- **THEN** the system MUST reject the request with HTTP 422 or appropriate error

### Requirement: Per-Model FAISS Indexes

Each registered model SHALL have its own dedicated FAISS `IndexFlatIP` index, persisted to disk as `faiss_{model_name}.index`. The index dimension MUST match the model's feature dimension.

- Index files: `faiss_xception.index` (2048-d), `faiss_resnet50.index` (2048-d), `faiss_clip.index` (512-d)
- Each index SHALL have its own `id_to_index` / `index_to_id` mapping persisted as `faiss_{model_name}.meta.pkl`
- `rebuild_from_db(model_name)` SHALL rebuild only that model's index from matching `FeatureVector` rows
- Index operations MUST be thread-safe (per-index lock)

#### Scenario: Rebuild filters by model name
- **WHEN** `rebuild_from_db("clip")` is called
- **THEN** only `FeatureVector` rows with `model_name="clip"` are loaded into the CLIP FAISS index

#### Scenario: Search uses correct model index
- **WHEN** a search request specifies `model=resnet50`
- **THEN** the query vector is searched in the ResNet50 FAISS index

### Requirement: Model-Aware Feature Storage

The `FeatureVector` table SHALL include a `model_name` column to identify which model produced the vector.

- Column: `model_name` — `String(50)`, NOT NULL, default `"xception"`
- Unique constraint on `(image_id, model_name)` to prevent duplicate per-model vectors
- Existing rows (no model_name) SHALL be treated as `model_name="xception"` after migration

#### Scenario: Ingest stores features for all models
- **WHEN** a POST /api/ingest request is made without a `model` parameter
- **THEN** one `FeatureVector` row per registered model SHALL be created for each image

#### Scenario: Ingest with specific model
- **WHEN** a POST /api/ingest request specifies `model=xception`
- **THEN** only one `FeatureVector` row with `model_name="xception"` SHALL be created

### Requirement: Model-Aware Search API

The `POST /api/search` endpoint SHALL accept an optional `model` query parameter.

- Default value: `"xception"`
- The query image's feature SHALL be extracted using the specified model
- The search SHALL use the corresponding model's FAISS index
- The response SHOULD include the `model` name used

#### Scenario: Search with model parameter
- **WHEN** a POST /api/search request includes `?model=clip`
- **THEN** the query is extracted with CLIP (512-d) and searched in the CLIP FAISS index
- **AND** the response includes `"model": "clip"`

#### Scenario: Search default model
- **WHEN** a POST /api/search request does not include a model parameter
- **THEN** the default `xception` model SHALL be used

### Requirement: List Models Endpoint

The system SHALL expose `GET /api/models` returning a JSON array of available model names.

#### Scenario: List available models
- **WHEN** a GET /api/models request is made
- **THEN** the response SHALL be `["xception", "resnet50", "clip"]`

### Requirement: Existing Data Compatibility

Existing FAISS index file at `data/faiss.index` SHALL be treated as `data/faiss_xception.index` on first startup after migration. Existing `FeatureVector` rows without `model_name` SHALL default to `"xception"`.

#### Scenario: Legacy index renamed
- **WHEN** the server starts and finds `data/faiss.index` but no `data/faiss_xception.index`
- **THEN** it SHALL rename `faiss.index` → `faiss_xception.index`

#### Scenario: Legacy feature vectors default
- **WHEN** querying FeatureVector rows created before the migration
- **THEN** `model_name` SHALL be `"xception"` for all such rows
