## Context

The existing system has a FastAPI backend with:
- `POST /api/ingest` — single-image upload with optional tags
- `POST /api/search` — image similarity search returning top-K results with distance

Both require a running server and browser. The CLI tool will reuse these endpoints via HTTP.

## Goals / Non-Goals

**Goals:**
- `cli.py ingest <dir>` — recursive scan of subdirectories, each subdirectory name = tag label, upload all images with that tag
- `cli.py search <dir>` — batch-search all images in `<dir>` against the DB, show top-5 per query with labels
- Use `argparse` subcommands with clear help text
- Output results to stdout in readable table format

**Non-Goals:**
- No changes to backend API or database schema
- No real-time progress bar (simple per-file status is fine)
- No authentication or authorization

## Decisions

1. **Separate `cli.py` in `backend/`** — sits alongside the backend code, calls it via HTTP. This keeps the CLI decoupled from the backend package.

2. **httpx (sync)** — already in dev dependencies; promote to main deps. Sync requests are simpler for a CLI script.

3. **Folder scan**: `ingest` uses `rglob` to find all images in subdirectories. Folder name = tag. Multiple tags supported: if folder is `animals/cats/`, tags become "animals, cats".

4. **Search output**: Table with columns `query_file | rank | match_file | label_tags | similarity%`. Printed to stdout.

5. **Error handling**: Per-file errors are printed to stderr, script continues to next file. Exit code 1 if all files fail.

## Risks / Trade-offs

- **Risk:** Large batch ingest floods the server. **Mitigation:** Sequential uploads with 0.1s delay between files to avoid overwhelming the server.
- **Risk:** Search on many query images is slow. **Mitigation:** Each query is an independent API call; acceptable for CLI use.
- **Trade-off:** httpx sync vs async — sync is simpler and sufficient for a CLI script.
