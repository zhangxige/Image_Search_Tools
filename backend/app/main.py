import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pillow_heif import register_heif_opener
register_heif_opener()

from app.config import UPLOAD_DIR, DATA_DIR
from app.database import init_db, SessionLocal
from app.models import ImageRecord, FeatureVector
from app.feature_extractor import get_available_models, extract_feature, get_model
from app.faiss_manager import load_index, rebuild_from_db, rename_legacy_index, add_to_index
from app.exif_utils import open_image
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


@app.get("/api/models")
def list_models():
    return JSONResponse(content=get_available_models())


@app.on_event("startup")
def on_startup():
    init_db()
    rename_legacy_index()

    db = SessionLocal()
    try:
        for model_name in get_available_models():
            load_index(model_name)
            try:
                get_model(model_name)
            except Exception:
                continue

            images_missing = (
                db.query(ImageRecord)
                .outerjoin(
                    FeatureVector,
                    (FeatureVector.image_id == ImageRecord.id)
                    & (FeatureVector.model_name == model_name),
                )
                .filter(FeatureVector.id.is_(None))
                .all()
            )

            if images_missing:
                import logging
                logging.getLogger(__name__).info(
                    f"Backfilling {len(images_missing)} images for model '{model_name}'..."
                )
                for img in images_missing:
                    try:
                        with db.begin_nested():
                            existing = db.query(FeatureVector.id).filter(
                                FeatureVector.image_id == img.id,
                                FeatureVector.model_name == model_name,
                            ).first()
                            if existing:
                                continue
                            full_path = UPLOAD_DIR / img.filename
                            if not full_path.exists():
                                continue
                            image = open_image(full_path.read_bytes(), img.filename)
                            feature = extract_feature(image, model_name)
                            fv = FeatureVector(
                                image_id=img.id,
                                vector=feature.tobytes(),
                                dimension=feature.shape[0],
                                model_name=model_name,
                            )
                            db.add(fv)
                            db.flush()
                            add_to_index(model_name, img.id, feature)
                    except Exception:
                        pass
                db.commit()

            try:
                count = rebuild_from_db(db, model_name)
            except Exception:
                count = 0
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Image Search Engine API"}
