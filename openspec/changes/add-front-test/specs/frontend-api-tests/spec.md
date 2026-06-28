## ADDED Requirements

### Requirement: Gallery page integration tests
The Gallery page SHALL fetch, display, filter, select, and delete images correctly via mocked API calls.

#### Scenario: Loads images on mount
- **WHEN** Gallery page mounts and mock returns 2 images
- **THEN** it SHALL display 2 image cards with correct filenames

#### Scenario: Pagination controls visible
- **WHEN** total image count exceeds page size (30)
- **THEN** pagination controls SHALL be rendered

#### Scenario: Tag filter filters results
- **WHEN** user types a tag filter term and 300ms debounce elapses
- **THEN** the page SHALL re-fetch images with the tag parameter and reset to page 1

#### Scenario: Select-all checkbox toggles all
- **WHEN** select-all checkbox is clicked
- **THEN** all visible image cards SHALL be selected

#### Scenario: Batch delete removes selected
- **WHEN** user selects multiple images and confirms batch delete
- **THEN** a DELETE request SHALL be sent with the selected image IDs

#### Scenario: Shows empty state
- **WHEN** API returns zero images
- **THEN** the page SHALL display an empty state message

### Requirement: Upload page integration tests
The Upload page SHALL handle drag-drop, file selection, tag input, and API submission correctly.

#### Scenario: Submits files with tags
- **WHEN** user selects files and enters tags, then submits
- **THEN** POST /api/ingest SHALL be called with the files and tags form data

#### Scenario: Shows success results
- **WHEN** API returns success for uploaded files
- **THEN** the page SHALL display result cards for each uploaded image

### Requirement: Search page integration tests
The Search page SHALL handle query image upload, search request, result display, and export.

#### Scenario: Disables search button when no images
- **WHEN** no query images have been selected
- **THEN** the search button SHALL be disabled

#### Scenario: Sends search request with top-K
- **WHEN** user uploads a query image and sets top-K to 5, then clicks search
- **THEN** POST /api/search SHALL be called with the image and `top_k=5`

#### Scenario: Displays search results
- **WHEN** API returns results for a search
- **THEN** each result SHALL display an image thumbnail and similarity percentage

### Requirement: Logs page integration tests
The Logs page SHALL fetch and display ingestion logs with pagination.

#### Scenario: Loads logs on mount
- **WHEN** Logs page mounts and mock returns 10 logs
- **THEN** the page SHALL display all 10 log entries

#### Scenario: Load more pagination
- **WHEN** user clicks "Load More" and more logs exist
- **THEN** additional log entries SHALL be appended to the list
