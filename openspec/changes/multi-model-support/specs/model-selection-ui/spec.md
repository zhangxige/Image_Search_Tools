## ADDED Requirements

### Requirement: Model Selector on Search Page

The frontend search page SHALL display a dropdown/select input labeled "Model" allowing the user to choose which feature extraction model to use for similarity search.

- Available options SHALL be fetched from `GET /api/models` at page load
- Default selection: `xception`
- The selected model SHALL be sent as the `model` field in the search form data
- The UI SHALL indicate which model was used for each search result set

#### Scenario: Dropdown populated from API
- **WHEN** the search page loads
- **THEN** it SHALL fetch `GET /api/models` and populate the model dropdown with the returned names

#### Scenario: Model sent with search request
- **WHEN** the user selects "clip" and clicks Search
- **THEN** the POST /api/search request SHALL include `model=clip`

### Requirement: CLI --model Flag

Both `ingest` and `search` CLI subcommands SHALL accept a `--model` option.

- `--model` SHALL accept one of: `xception`, `resnet50`, `clip`
- Default: `xception`
- `ingest --model clip` SHALL only extract CLIP features for the uploaded images
- `search --model clip` SHALL search using the CLIP FAISS index
- `ingest` without `--model` SHALL extract for ALL registered models (matching API default behavior)

#### Scenario: CLI search with custom model
- **WHEN** `python cli.py search /path/to/queries --model resnet50`
- **THEN** the CLI SHALL send `model=resnet50` with the POST /api/search request

#### Scenario: CLI ingest with specific model
- **WHEN** `python cli.py ingest /path/to/dataset --model clip`
- **THEN** the CLI SHALL send `model=clip` with the POST /api/ingest request

#### Scenario: CLI ingest defaults to all models
- **WHEN** `python cli.py ingest /path/to/dataset` is run without `--model`
- **THEN** the CLI SHALL NOT include a `model` field in the ingest request (API defaults to all models)
