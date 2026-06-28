from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'images.db'}"
FAISS_INDEX_PATH = DATA_DIR / "faiss.index"
VECTOR_DIM = 2048
IMG_SIZE = 299
TOP_K = 5
