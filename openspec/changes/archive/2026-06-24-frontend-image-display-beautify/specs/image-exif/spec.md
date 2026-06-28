## ADDED Requirements

### Requirement: Backend extracts EXIF at ingest time
The system SHALL extract EXIF metadata from uploaded image files during the ingest process using Pillow.

#### Scenario: EXIF extracted on ingest
- **WHEN** an image with EXIF data is uploaded via `POST /api/ingest`
- **THEN** the system SHALL extract camera Make, Model, Aperture, ShutterSpeed, ISO, FocalLength, DateTimeOriginal, and GPSInfo (if present)

#### Scenario: Image without EXIF
- **WHEN** an image without EXIF metadata is uploaded
- **THEN** the system SHALL store `null` in the `exif_data` column without error

#### Scenario: Embedded thumbnail tags excluded
- **WHEN** EXIF data contains embedded thumbnail tags (tag IDs 513, 514)
- **THEN** the system SHALL strip those tags from the stored EXIF data

### Requirement: Backend stores EXIF in JSON column
The system SHALL store extracted EXIF metadata in a nullable JSON column `exif_data` on the `ImageRecord` model.

#### Scenario: JSON column exists
- **WHEN** the database migration runs
- **THEN** the `images` table SHALL have a nullable `exif_data` JSON column

#### Scenario: EXIF data is serialized
- **WHEN** EXIF data is stored
- **THEN** it SHALL be serialized as a JSON object with human-readable tag names mapped to values

### Requirement: Backend exposes EXIF via API
The system SHALL provide a `GET /api/images/{id}/exif` endpoint that returns EXIF metadata for a given image.

#### Scenario: EXIF data exists
- **WHEN** a GET request is made to `/api/images/{id}/exif` for an image with stored EXIF
- **THEN** the response SHALL have status 200 and return a JSON object with `hasExif: true` and the EXIF data

#### Scenario: No EXIF data (legacy image)
- **WHEN** a GET request is made for an image with `exif_data = null`
- **THEN** the system SHALL attempt on-the-fly extraction from the stored file, cache the result in the DB, and return it

#### Scenario: No EXIF and file missing
- **WHEN** the stored file cannot be found for on-the-fly extraction
- **THEN** the response SHALL return JSON `{"hasExif": false}` with status 200

#### Scenario: Image not found
- **WHEN** a GET request is made for a non-existent image ID
- **THEN** the response SHALL have status 404

### Requirement: EXIF response schema
The EXIF endpoint SHALL return a JSON response with camera metadata mapped to human-readable keys.

#### Scenario: EXIF response structure
- **WHEN** EXIF data is available
- **THEN** the response SHALL include fields: `make`, `model`, `aperture`, `shutterSpeed`, `iso`, `focalLength`, `dateTaken`, `dimensions`, `hasExif: true`

### Requirement: Backend tag mapping
The system SHALL map numeric EXIF tag IDs to human-readable string keys.

#### Scenario: Tag mapping
- **WHEN** EXIF extraction runs
- **THEN** tag 271 SHALL map to `make`, 272 to `model`, 33434 to `aperture`, 33437 to `shutterSpeed`, 34855 to `iso`, 37386 to `focalLength`, 306 to `dateTaken`
