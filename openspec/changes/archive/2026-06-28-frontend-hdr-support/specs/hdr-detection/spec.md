## ADDED Requirements

### Requirement: Backend detects HDR at ingest time
The system SHALL detect whether an uploaded image is HDR by analyzing EXIF metadata during the ingest process.

#### Scenario: HDR detected via ColorSpace tag
- **WHEN** the EXIF ColorSpace tag (40961) has value 2 (Adobe RGB) or 65535 (Uncalibrated) with an ICC profile indicating wide gamut
- **THEN** the system SHALL mark the image as HDR

#### Scenario: HDR detected via Gamma tag
- **WHEN** the EXIF Gamma tag (42240) indicates a value below 1.0 (typical SDR) or matches HDR transfer function values
- **THEN** the system SHALL mark the image as HDR

#### Scenario: HDR detected via file format
- **WHEN** the uploaded file has extension .heic, .heif, or .avif
- **THEN** the system SHALL attempt HDR detection with higher confidence

#### Scenario: HDR detected via maker notes
- **WHEN** the EXIF MakerNote tag (37500) contains phone-specific HDR indicators (e.g., "HDR" substring, "HDR10+" for Samsung, "PortraitHDR" for Apple)
- **THEN** the system SHALL mark the image as HDR and extract the format label

#### Scenario: Non-HDR image
- **WHEN** none of the HDR indicators are found
- **THEN** the system SHALL store `is_hdr = False` and `hdr_format = null`

### Requirement: Backend stores HDR metadata
The system SHALL store HDR detection results in two columns on the `ImageRecord` model.

#### Scenario: HDR columns exist
- **WHEN** the database migration runs
- **THEN** the `images` table SHALL have `is_hdr` Boolean (default false, indexed) and `hdr_format` String(50) (nullable) columns

#### Scenario: HDR data is stored during ingest
- **WHEN** an HDR image is ingested
- **THEN** the system SHALL set `is_hdr = True` and `hdr_format` to a human-readable label (e.g., "Apple HEIC", "Samsung HDR10+", "AVIF HDR")

### Requirement: API exposes HDR flags
The system SHALL include HDR metadata in the `ImageResponse` schema.

#### Scenario: ImageResponse includes HDR fields
- **WHEN** the frontend calls `GET /api/images`
- **THEN** each image object SHALL include `is_hdr: bool` and `hdr_format: Optional[str]`

#### Scenario: HDR images filterable
- **WHEN** a user wants to filter by HDR images
- **THEN** the system MAY support a future query parameter `hdr=true`
