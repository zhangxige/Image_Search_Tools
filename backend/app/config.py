from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'images.db'}"
TOP_K = 5
