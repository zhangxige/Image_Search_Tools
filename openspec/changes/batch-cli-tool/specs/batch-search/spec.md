## ADDED Requirements

### Requirement: CLI batch-searches images
The system SHALL provide a CLI command to batch-search local images against the database.

#### Scenario: Batch search
- **WHEN** the user runs `python cli.py search /path/to/queries/`
- **THEN** the script SHALL scan the directory for all supported image files
- **AND** for each image, call `POST /api/search` with `top_k=5`
- **AND** print results in a table with columns: `query_file | rank | match_file | tags | similarity%`

#### Scenario: Custom top-K
- **WHEN** the user specifies `-k 10` or `--top-k 10`
- **THEN** the script SHALL use that value instead of the default 5

#### Scenario: Supported image formats
- **WHEN** scanning the query directory
- **THEN** the script SHALL include files with extensions: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.heic`, `.heif`, `.avif`

#### Scenario: Error handling
- **WHEN** a query image fails to search
- **THEN** the script SHALL print the error to stderr and continue with next file

### Requirement: Common CLI options

#### Scenario: Custom server URL
- **WHEN** the user passes `--url http://other-server:8000`
- **THEN** the script SHALL use that URL instead of `http://localhost:8000`

#### Scenario: Help
- **WHEN** the user runs `python cli.py search --help`
- **THEN** the script SHALL display clear usage information
