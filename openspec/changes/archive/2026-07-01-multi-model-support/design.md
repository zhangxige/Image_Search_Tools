## Context

Currently the engine uses a module-level singleton `feature_extractor.py` that loads only Xception. All ingest and search paths call `extract_feature(image)`, producing a 2048-d vector stored in a single FAISS `IndexFlatIP(2048)`. Both the `FeatureVector` table and the FAISS index are model-agnostic — there is no way to tell which model produced a given vector.

All three target models (Xception, ResNet50, CLIP) produce L2-normalized vectors, making cosine similarity via `IndexFlatIP` viable for all. However, dimensions differ (2048 vs 512), requiring separate FAISS indexes.

## Goals / Non-Goals

**Goals:**
- Support Xception (2048-d), ResNet50 (2048-d), and CLIP ViT-B/32 (512-d) as feature extractors
- New images ingested store features for ALL registered models by default (future-proof search)
- API search accepts `?model=` parameter to select which model to query
- CLI subcommands gain `--model` flag (default: `xception`)
- Frontend search page has a model dropdown
- Old data (no `model_name`) is treated as `xception` automatically
- Thread-safe model loading and index access

**Non-Goals:**
- Model training or fine-tuning (all models are used frozen/pretrained)
- Removing Xception or making it non-default
- Multi-modal search (text-to-image via CLIP — future work)
- Multiple models in a single search query

## Decisions

### 1. Model Registry via Dictionary, Not Inheritance

A `MODEL_REGISTRY` dict maps `model_name` → config + lazy loader, rather than a polymorphic `BaseExtractor` class hierarchy.

- **Why**: Simpler. Each model has a different init pattern (timm vs transformers), different input transforms, and different forward passes. A common base class would leak abstractions. The dict approach lets each model define its own `load_fn()` closure.
- **Alternative considered**: Abstract base class with `load_model()`, `preprocess()`, `extract()` methods. Rejected because models would need awkward shared signatures (e.g., CLIP needs tokenizer for text, even though we only use vision).

### 2. Per-Model FAISS Index Files

Each model gets its own `faiss_{model_name}.index` and `faiss_{model_name}.meta.pkl` on disk.

- **Why**: Dimensions differ (2048 vs 512); FAISS `IndexFlatIP` is fixed-dimension. Separate files avoid dimension mismatch and make it easy to rebuild one model without affecting others.
- **Alternative considered**: Single FAISS index padded to max dimension. Rejected — wastes memory, adds complexity in masking, and hurts search quality.

### 3. Ingest Extracts for ALL Models by Default

`POST /api/ingest` without a `model` parameter extracts features for every registered model and inserts one `FeatureVector` row per model.

- **Why**: Once stored, any model can be used for search without re-ingesting. The per-row cost is small (a few KB per model per image).
- **Trade-off**: Ingest is 3× slower (one forward pass per model). This is acceptable for an offline/batch ingest tool; users who want speed can pass `?model=xception`.

### 4. Model Name in FeatureVector as Simple String Column

`FeatureVector.model_name` is a `String(50)` column defaulting to `"xception"`.

- **Why**: Simple, indexable, no join overhead. A single `(image_id, model_name)` unique constraint prevents duplicates.
- **Alternative**: Separate `FeatureVectorXception`, `FeatureVectorResNet50` tables. Rejected — adds schema complexity and makes cross-model queries impossible.

### 5. transformers for CLIP, timm for ResNet50

CLIP uses `transformers` library (`CLIPModel`, `CLIPProcessor`); ResNet50 uses `timm` (already a dependency).

- **Why**: `timm` already exists for Xception. `transformers` is the canonical library for CLIP. Both provide pretrained weights with a single line.
- **Trade-off**: `transformers` adds ~500 MB to the environment. This is acceptable for the added capability.

## Risks / Trade-offs

- **[Dimension mismatch on FAISS rebuild]** `rebuild_from_db()` must filter by `model_name`. → Mitigation: pass `model_name` parameter; each model's rebuild only queries rows matching that model.
- **[Ingest performance]** 3 forward passes per image. → Mitigation: models are loaded lazily and reused; ingest is inherently I/O-bound anyway.
- **[CLIP startup time]** Loading `transformers` CLIP adds ~2-3s cold start. → Mitigation: lazy loading (only loads when first used).
- **[Frontend UX]** User selects a model but results might be stale if only one model was ingested. → Mitigation: always ingest for all models by default; show a warning if search returns empty for a model.
- **[DB migration]** Existing `FeatureVector` rows have no `model_name`. → Mitigation: add column with default `"xception"`; old FAISS index file is treated as `faiss_xception.index`.

## Migration Plan

1. Deploy backend code changes (new model registry, updated ingest/search routers)
2. Backfill: `ALTER TABLE feature_vectors ADD COLUMN model_name VARCHAR(50) NOT NULL DEFAULT 'xception'`
3. Rename existing `faiss.index` → `faiss_xception.index` on next startup
4. Old CLI clients without `--model` continue to work (default = `xception`)

Rollback: revert code; rename `faiss_xception.index` back to `faiss.index`; no data loss.

## Open Questions

- Should we also support text-to-image search with CLIP in this change? → Decision: No, out of scope. This change only uses CLIP's vision encoder (image-to-image).
- Should the frontend fetch the list of available models from the API? → Yes. Add `GET /api/models` returning `["xception", "resnet50", "clip"]`.
