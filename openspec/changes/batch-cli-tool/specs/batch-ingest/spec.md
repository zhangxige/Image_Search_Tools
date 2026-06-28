## ADDED Requirements

### Requirement: CLI ingests labeled folders
The system SHALL provide a CLI command to batch-ingest images from folders where folder names become tags.

#### Scenario: Ingest a labeled folder
- **WHEN** the user runs `python cli.py ingest /path/to/dataset`
- **THEN** the script SHALL scan all subdirectories recursively
- **AND** each subdirectory name SHALL be used as a tag for images inside it
- **AND** nested paths SHALL produce comma-separated tags (e.g., `animals/cats/` → `animals, cats`)
- **AND** each image SHALL be uploaded via `POST /api/ingest` with those tags

#### Scenario: Supported image formats
- **WHEN** scanning folders
- **THEN** the script SHALL include files with extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.heic`, `.heif`, `.avif`

#### Scenario: Error handling
- **WHEN** an image fails to upload
- **THEN** the script SHALL print the error to stderr and continue with next file
- **AND** at the end, print a summary of success/failure counts

### Requirement: Common CLI options

#### Scenario: Custom server URL
- **WHEN** the user passes `--url http://other-server:8000`
- **THEN** the script SHALL use that URL instead of `http://localhost:8000`

#### Scenario: Help
- **WHEN** the user runs `python cli.py --help` or `python cli.py ingest --help`
- **THEN** the script SHALL display clear usage information
