import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pillow_heif import register_heif_opener

register_heif_opener()

from app.config import UPLOAD_DIR, DATA_DIR, VECTOR_DIM
from app.database import init_db, SessionLocal
from app.models import ImageRecord, FeatureVector
from app.faiss_manager import load_index, build_index, get_index
from app.routers import ingest, search, images

app = FastAPI(title="Image Search Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(images.router)


@app.on_event("startup")
def on_startup():
    init_db()
    load_index()

    if get_index().ntotal == 0:
        db = SessionLocal()
        try:
            records = db.query(ImageRecord, FeatureVector).join(FeatureVector).all()
            if records:
                ids = []
                vectors = []
                for rec, feat in records:
                    ids.append(rec.id)
                    vec = np.frombuffer(feat.vector, dtype=np.float32)
                    vectors.append(vec)
                build_index(ids, np.array(vectors))
        finally:
            db.close()


@app.get("/")
def root():
    return {"message": "Image Search Engine API"}
