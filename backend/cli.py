import argparse
import sys
from pathlib import Path
import httpx

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic", ".heif", ".avif"}


def build_tags(dir_path: Path, root: Path) -> str:
    parts = dir_path.relative_to(root).parts
    return ", ".join(parts)


def do_ingest(args: argparse.Namespace) -> None:
    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f"Error: {args.directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    url = args.url.rstrip("/")
    total = 0
    ok = 0
    fail = 0
    params = {}
    if args.model:
        params["model"] = args.model

    for dir_path in sorted(root.iterdir()):
        if not dir_path.is_dir():
            continue
        tags = build_tags(dir_path, root)
        image_files = sorted(
            p for p in dir_path.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not image_files:
            continue

        for file_path in image_files:
            total += 1
            try:
                with open(file_path, "rb") as f:
                    files = {"files": (file_path.name, f, "image/" + file_path.suffix.lstrip("."))}
                    data = {"tags": tags}
                    resp = httpx.post(f"{url}/api/ingest", params=params, files=files, data=data, timeout=120)
                    if resp.is_success:
                        ok += 1
                        print(f"  ✓ {file_path.relative_to(root)}")
                    else:
                        fail += 1
                        print(f"  ✗ {file_path.relative_to(root)} — {resp.status_code} {resp.text}", file=sys.stderr)
            except Exception as e:
                fail += 1
                print(f"  ✗ {file_path.relative_to(root)} — {e}", file=sys.stderr)

    print(f"\nDone: {ok} succeeded, {fail} failed, {total} total")


def do_search(args: argparse.Namespace) -> None:
    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f"Error: {args.directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    url = args.url.rstrip("/")
    top_k = args.top_k
    model = args.model
    params = {"model": model}

    image_files = sorted(
        p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not image_files:
        print("No images found in the specified directory")
        return

    for file_path in image_files:
        print(f"\nQuery: {file_path.name}")
        try:
            with open(file_path, "rb") as f:
                files = {"files": (file_path.name, f, "image/" + file_path.suffix.lstrip("."))}
                data = {"top_k": str(top_k)}
                resp = httpx.post(f"{url}/api/search", params=params, files=files, data=data, timeout=120)
                if not resp.is_success:
                    print(f"  Error: {resp.status_code} {resp.text}", file=sys.stderr)
                    continue
                results = resp.json().get("results", [])
                if not results:
                    print("  No matches found")
                else:
                    print(f"  {'Rank':<5} {'Match File':<40} {'Tags':<30} {'Similarity':<10}")
                    print(f"  {'-'*84}")
                    for i, r in enumerate(results, 1):
                        img = r["image"]
                        sim = r["distance"] * 100
                        print(f"  {i:<5} {img['original_filename']:<40} {img['tags']:<30} {sim:.1f}%")
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Image Search CLI — batch ingest and search")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend server URL (default: http://localhost:8000)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    ingest_parser = subparsers.add_parser("ingest", help="Batch-ingest images from labeled folders")
    ingest_parser.add_argument("directory", help="Root directory containing labeled subfolders (folder names = tags)")
    ingest_parser.add_argument("--model", choices=["xception", "resnet50", "clip"], default=None,
                               help="Model to use (default: all models)")
    ingest_parser.set_defaults(func=do_ingest)

    search_parser = subparsers.add_parser("search", help="Batch-search images against the database")
    search_parser.add_argument("directory", help="Directory containing query images")
    search_parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of top results per query (default: 5)")
    search_parser.add_argument("--model", choices=["xception", "resnet50", "clip"], default="xception",
                               help="Feature extraction model (default: xception)")
    search_parser.set_defaults(func=do_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
