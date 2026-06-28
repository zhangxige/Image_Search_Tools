## Why

Currently all operations (ingest, search) require the web UI and a running backend server. There is no way to batch-process local images from the command line. Users need a CLI tool for two common workflows: bulk-ingesting labeled image folders, and batch-searching images against the database.

## What Changes

- New Python CLI script `cli.py` using `argparse` with two subcommands:
  - `ingest`: Batch-import images from folders where folder name = label/tag
  - `search`: Batch-compare local images against the database, returning top-5 results per image with labels
- The CLI calls the existing FastAPI backend endpoints via HTTP (httpx)
- No changes to the existing backend API — the CLI is an alternative frontend

## Capabilities

### New Capabilities
- `batch-ingest`: Import images from labeled folders (folder name = tag) into the image database
- `batch-search`: Run multiple query images against the search API and aggregate result labels

### Modified Capabilities
None — existing backend API is unchanged

## Impact

- New file: `backend/cli.py` — the CLI entry point
- New dependency: `httpx` (already in dev deps, promote to main deps)
- No changes to existing backend routes, models, or frontend
