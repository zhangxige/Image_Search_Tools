## ADDED Requirements

### Requirement: Ingest endpoint accepts valid uploads
The `POST /api/ingest` endpoint SHALL accept image file uploads, create database records, and return success status.

#### Scenario: Successful single image ingestion
- **WHEN** a valid image file is uploaded to `POST /api/ingest`
- **THEN** the response SHALL have status 200 and `success` list containing the ingested image with `id`, `filename`, `original_filename`

#### Scenario: Successful ingestion with tags
- **WHEN** a valid image file is uploaded to `POST /api/ingest` with a `tags` form field
- **THEN** the response SHALL have status 200 and the ingested image record SHALL contain the provided tags

#### Scenario: Batch ingestion of multiple images
- **WHEN** multiple valid image files are uploaded to `POST /api/ingest`
- **THEN** the response SHALL have status 200 and `success` list SHALL contain all ingested images

#### Scenario: Ingestion with invalid file returns error
- **WHEN** a non-image file is uploaded to `POST /api/ingest`
- **THEN** the response SHALL have status 200 and the file SHALL appear in the `failed` list with an error message

### Requirement: Search endpoint returns ranked results
The `POST /api/search` endpoint SHALL accept query images and return ranked similar images.

#### Scenario: Search with single query image
- **WHEN** at least one image exists in the database and a valid image is uploaded to `POST /api/search`
- **THEN** the response SHALL have status 200 and contain a `results` array with each result having `image` (ImageResponse) and `distance` (float)

#### Scenario: Search with top_k parameter
- **WHEN** a search request includes `top_k=3`
- **THEN** the response SHALL contain at most 3 results

#### Scenario: Search with no matching images
- **WHEN** the database is empty and a valid image is uploaded to `POST /api/search`
- **THEN** the response SHALL have status 200 and contain an empty `results` array

#### Scenario: Search with invalid file returns error
- **WHEN** a non-image file is uploaded to `POST /api/search`
- **THEN** the response SHALL have status 422 or an appropriate error

### Requirement: List images endpoint supports pagination and filtering
The `GET /api/images` endpoint SHALL return paginated image records with optional tag filtering.

#### Scenario: List all images returns paginated results
- **WHEN** `GET /api/images` is called with `skip=0&limit=10`
- **THEN** the response SHALL have status 200 and return an array of `ImageResponse` objects, with at most 10 items

#### Scenario: List images filtered by tag
- **WHEN** `GET /api/images` is called with `tag=landscape`
- **THEN** the response SHALL contain only images whose tags field contains "landscape"

#### Scenario: List images with skip parameter
- **WHEN** `GET /api/images` is called with `skip=5&limit=10`
- **THEN** the response SHALL skip the first 5 images and return the next page

### Requirement: Count images endpoint works
The `GET /api/images/count` endpoint SHALL return the total count of images, optionally filtered by tag.

#### Scenario: Count all images
- **WHEN** `GET /api/images/count` is called
- **THEN** the response SHALL have status 200 and contain an integer count

#### Scenario: Count images filtered by tag
- **WHEN** `GET /api/images/count` is called with `tag=portrait`
- **THEN** the response SHALL return the count of images matching that tag

### Requirement: Delete endpoints remove images correctly
The `DELETE /api/images/{id}` and `DELETE /api/images` endpoints SHALL remove image records and rebuild the FAISS index.

#### Scenario: Delete single existing image
- **WHEN** `DELETE /api/images/1` is called for an existing image
- **THEN** the response SHALL have status 200 and the image SHALL no longer exist in the database

#### Scenario: Delete single non-existent image returns 404
- **WHEN** `DELETE /api/images/9999` is called for a non-existent image
- **THEN** the response SHALL have status 404

#### Scenario: Batch delete multiple images
- **WHEN** `DELETE /api/images?image_ids=1&image_ids=2` is called
- **THEN** the response SHALL have status 200 and the deleted images SHALL no longer exist in the database

#### Scenario: Batch delete with mix of existing and non-existing
- **WHEN** `DELETE /api/images?image_ids=1&image_ids=9999` is called
- **THEN** the response SHALL return both `deleted` and `not_found` lists

### Requirement: Update image endpoint modifies tags
The `PATCH /api/images/{id}` endpoint SHALL update image metadata.

#### Scenario: Update tags on existing image
- **WHEN** `PATCH /api/images/1` is called with `{"tags": "nature,sky"}`
- **THEN** the response SHALL have status 200 and the image's tags SHALL be updated to "nature,sky"

#### Scenario: Update non-existent image returns 404
- **WHEN** `PATCH /api/images/9999` is called
- **THEN** the response SHALL have status 404

### Requirement: Logs endpoint returns ingestion logs
The `GET /api/images/logs` endpoint SHALL return paginated ingestion log records.

#### Scenario: List logs returns paginated results
- **WHEN** `GET /api/images/logs` is called with `skip=0&limit=10`
- **THEN** the response SHALL have status 200 and return an array of `IngestionLogResponse` objects

#### Scenario: Logs are created after successful ingestion
- **WHEN** an image is successfully ingested via `POST /api/ingest`
- **THEN** a corresponding log entry SHALL exist in the logs endpoint response
