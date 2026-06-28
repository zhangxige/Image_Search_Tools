## ADDED Requirements

### Requirement: Models have correct ORM mapping
The SQLAlchemy model classes (`ImageRecord`, `FeatureVector`, `IngestionLog`) SHALL define columns matching the production schema, with correct types, constraints, and relationships.

#### Scenario: ImageRecord has all columns
- **WHEN** an `ImageRecord` instance is created with valid field values
- **THEN** all columns (`id`, `filename`, `original_filename`, `file_size`, `width`, `height`, `mime_type`, `tags`, `created_at`) SHALL be accessible and match the supplied values

#### Scenario: ImageRecord cascades to FeatureVector
- **WHEN** an `ImageRecord` is deleted
- **THEN** its associated `FeatureVector` SHALL be automatically deleted from the database

#### Scenario: FeatureVector stores binary vector data
- **WHEN** a `FeatureVector` is created with a numpy float32 array serialized to bytes
- **THEN** the `vector` field SHALL store the bytes and deserialize back to an array of the same shape

#### Scenario: IngestionLog links to ImageRecord
- **WHEN** an `IngestionLog` is created with an `image_id` referencing an existing `ImageRecord`
- **THEN** the relationship `log.image` SHALL return the associated `ImageRecord`

### Requirement: Pydantic schemas validate correctly
Request and response schemas SHALL validate inputs and serialize outputs according to their field definitions.

#### Scenario: ImageResponse serializes an ImageRecord
- **WHEN** an `ImageResponse` is constructed from a valid `ImageRecord` instance
- **THEN** it SHALL produce a dict with all expected keys and correct value types

#### Scenario: ImageUpdate accepts partial fields
- **WHEN** an `ImageUpdate` is created with only `tags` set
- **THEN** it SHALL validate without error and `tags` SHALL be `None` if omitted

#### Scenario: SearchResult schema
- **WHEN** a `SearchResult` is constructed with an `ImageResponse` and a float distance
- **THEN** the `distance` field SHALL be a float between 0 and 1

### Requirement: FAISS manager builds and searches correctly
The `faiss_manager` module SHALL build an IndexFlatIP index, add vectors, and return ranked results.

#### Scenario: Build index with correct dimension
- **WHEN** `build_index(2048)` is called
- **THEN** the returned index SHALL be a FAISS index with dimension 2048

#### Scenario: Add vector and search returns it
- **WHEN** a vector is added with `add_to_index(vec, img_id)` and `search(vec, top_k=1)` is called
- **THEN** the result SHALL contain the image_id and a similarity distance

#### Scenario: Search with top_k returns correct count
- **WHEN** 5 vectors are added and `search(vec, top_k=3)` is called
- **THEN** the result SHALL contain exactly 3 results (or fewer if insufficient vectors match)

#### Scenario: Rebuild from database produces the correct index
- **WHEN** `rebuild_from_db()` is called with a list of (id, vector) pairs
- **THEN** the index SHALL contain exactly those vectors

### Requirement: Feature extractor handles images correctly
The `feature_extractor` module SHALL extract 2048-d L2-normalized features from PIL Images and file paths.

#### Scenario: Extract feature from PIL Image
- **WHEN** a valid PIL Image is passed to `extract_feature(image)`
- **THEN** the returned numpy array SHALL have shape `(2048,)` and L2 norm of approximately 1.0

#### Scenario: Extract feature from file path
- **WHEN** a valid image file path is passed to `extract_feature_from_path(path)`
- **THEN** the returned numpy array SHALL have shape `(2048,)` and L2 norm of approximately 1.0

#### Scenario: Extract feature with invalid image raises error
- **WHEN** a corrupted or non-image file is passed to `extract_feature`
- **THEN** an exception SHALL be raised
