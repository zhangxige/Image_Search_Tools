## 1. Setup

- [x] 1.1 Create `backend/cli.py` with argparse structure and subcommands (ingest, search)
- [x] 1.2 Promote `httpx` from dev to main dependencies in `pyproject.toml`

## 2. Ingest Command

- [x] 2.1 Implement `do_ingest(args)` — scan subdirectories of the given path
- [x] 2.2 Build tag string from directory path (e.g., `animals/cats/` → `animals, cats`)
- [x] 2.3 Upload each image via `POST /api/ingest` with the tag string
- [x] 2.4 Print per-file progress and final summary (success/fail counts)

## 3. Search Command

- [x] 3.1 Implement `do_search(args)` — scan query directory for all supported images
- [x] 3.2 For each query image, call `POST /api/search` with `top_k=args.top_k`
- [x] 3.3 Print results table with columns: query_file, rank, match_file, tags, similarity%
- [x] 3.4 Support `-k` / `--top-k` option with default 5

## 4. Common Options

- [x] 4.1 Add `--url` option to override the backend base URL (default `http://localhost:8000`)
- [x] 4.2 Add help text for all subcommands and options
- [x] 4.3 Ensure error handling: per-file errors go to stderr, script continues

## 5. Verification

- [x] 5.1 Run `python cli.py --help` and verify both subcommands appear
- [x] 5.2 Run `python cli.py ingest --help` and `python cli.py search --help`
- [x] 5.3 Test ingest with a small labeled folder, verify images appear in web UI
- [x] 5.4 Test search with a query image, verify results table prints correctly
- [x] 5.5 Test `--url` with an alternative server URL
