import os
import io
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from PIL import Image

from app.database import get_db
from app.models import ImageRecord, FeatureVector, IngestionLog
from app.schemas import ImageResponse, ImageUpdate, IngestionLogResponse, ExifResponse
from app.config import UPLOAD_DIR
from app.faiss_manager import rebuild_from_db
from app.feature_extractor import get_available_models
from app.exif_utils import extract_exif, open_image

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("", response_model=List[ImageResponse])
def list_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ImageRecord)
    if tag:
        for t in tag.split(","):
            t = t.strip()
            if t:
                query = query.filter(ImageRecord.tags.contains(t))
    records = query.order_by(ImageRecord.created_at.desc()).offset(skip).limit(limit).all()
    return [ImageResponse.model_validate(r) for r in records]


@router.get("/count")
def count_images(
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ImageRecord)
    if tag:
        for t in tag.split(","):
            t = t.strip()
            if t:
                query = query.filter(ImageRecord.tags.contains(t))
    count = query.count()
    return {"count": count}


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = UPLOAD_DIR / record.filename
    if file_path.exists():
        os.remove(file_path)

    db.delete(record)
    db.commit()

    for m in get_available_models():
        rebuild_from_db(db, m)

    return {"message": "Image deleted", "id": image_id}


@router.delete("", status_code=200)
def batch_delete_images(image_ids: list[int] = Query(...), db: Session = Depends(get_db)):
    deleted = []
    not_found = []

    for image_id in image_ids:
        record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
        if not record:
            not_found.append(image_id)
            continue

        file_path = UPLOAD_DIR / record.filename
        if file_path.exists():
            os.remove(file_path)

        db.delete(record)
        deleted.append(image_id)

    db.commit()

    if deleted:
        for m in get_available_models():
            rebuild_from_db(db, m)

    return {"deleted": deleted, "not_found": not_found}


@router.patch("/{image_id}", response_model=ImageResponse)
def update_image(image_id: int, update: ImageUpdate, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    if update.tags is not None:
        record.tags = update.tags

    db.commit()
    db.refresh(record)
    return ImageResponse.model_validate(record)


@router.get("/logs", response_model=List[IngestionLogResponse])
def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    logs = db.query(IngestionLog).order_by(IngestionLog.created_at.desc()).offset(skip).limit(limit).all()
    return [IngestionLogResponse.model_validate(l) for l in logs]


BROWSER_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
HEIC_FORMATS = {".heic", ".heif", ".heics", ".avif"}


@router.get("/{image_id}/exif", response_model=ExifResponse)
def get_image_exif(image_id: int, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    exif = record.exif_data
    if exif is not None:
        clean = {k: v for k, v in exif.items() if not k.startswith("_")}
        return ExifResponse(hasExif=True, **clean)

    file_path = UPLOAD_DIR / record.filename
    if not file_path.exists():
        return ExifResponse(hasExif=False)

    exif = extract_exif(file_path)
    if exif:
        clean = {k: v for k, v in exif.items() if not k.startswith("_")}
        record.exif_data = exif
        db.commit()
        return ExifResponse(hasExif=True, **clean)

    return ExifResponse(hasExif=False)


@router.post("/preview")
def image_preview(file: UploadFile = File(...)):
    contents = file.file.read()
    image = open_image(contents, file.filename).convert("RGB")
    buf = io.BytesIO()
    image.save(buf, "JPEG", quality=85)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")


@router.get("/{image_id}/file")
def get_image_file(image_id: int, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(str(UPLOAD_DIR)) / record.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    ext = file_path.suffix.lower()

    if ext in BROWSER_FORMATS:
        return StreamingResponse(open(file_path, "rb"), media_type=f"image/{ext.lstrip('.')}")

    if ext in HEIC_FORMATS:
        img = Image.open(file_path).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=92)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/jpeg")

    return StreamingResponse(open(file_path, "rb"), media_type="application/octet-stream")
