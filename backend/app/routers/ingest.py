import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from PIL import Image
import io

from app.database import get_db
from app.models import ImageRecord, FeatureVector, IngestionLog
from app.schemas import IngestionResult, ImageResponse
from app.feature_extractor import extract_feature
from app.faiss_manager import add_to_index
from app.config import UPLOAD_DIR
from app.exif_utils import extract_exif, detect_hdr, heif_to_pil_with_exif

_HEIF_EXTS = {".heic", ".heif", ".heics", ".avif"}

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


def _process_image(file: UploadFile, db: Session, tags: str = ""):
    contents = file.file.read()
    ext = Path(file.filename).suffix or ".jpg"

    if ext.lower() in _HEIF_EXTS:
        image, exif_bytes = heif_to_pil_with_exif(contents)
        image = image.convert("RGB")
    else:
        img = Image.open(io.BytesIO(contents))
        exif_bytes = img.info.get("exif")
        image = img.convert("RGB")

    width, height = image.size

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    with open(file_path, "wb") as f:
        f.write(contents)

    exif_data = extract_exif(file_path)

    is_hdr, hdr_format = detect_hdr(exif_data, file.content_type, ext)

    needs_convert = ext.lower() in _HEIF_EXTS
    if needs_convert:
        jpeg_name = f"{uuid.uuid4().hex}.jpg"
        jpeg_path = UPLOAD_DIR / jpeg_name
        save_kw = {"format": "JPEG", "quality": 95}
        if exif_bytes:
            save_kw["exif"] = exif_bytes
        image.save(jpeg_path, **save_kw)
        file_path.unlink()
        unique_name = jpeg_name
        file_path = jpeg_path
        new_file_size = jpeg_path.stat().st_size
        stored_mime = "image/jpeg"
    else:
        new_file_size = len(contents)
        stored_mime = file.content_type

    feature = extract_feature(image)

    db_record = ImageRecord(
        filename=unique_name,
        original_filename=file.filename,
        file_size=new_file_size,
        width=width,
        height=height,
        mime_type=stored_mime,
        tags=tags,
        exif_data=exif_data,
        is_hdr=is_hdr,
        hdr_format=hdr_format,
    )
    db.add(db_record)
    db.flush()

    feature_blob = feature.tobytes()
    db_feature = FeatureVector(
        image_id=db_record.id,
        vector=feature_blob,
        dimension=2048,
    )
    db.add(db_feature)

    db_log = IngestionLog(
        operation="ingest",
        status="success",
        image_id=db_record.id,
        filename=file.filename,
        message="Image ingested successfully",
    )
    db.add(db_log)

    db.commit()

    add_to_index(db_record.id, feature)

    return ImageResponse.model_validate(db_record)


@router.post("", response_model=IngestionResult)
def ingest_images(
    files: list[UploadFile] = File(...),
    tags: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    success = []
    failed = []

    for file in files:
        try:
            result = _process_image(file, db, tags or "")
            success.append(result)
        except Exception as e:
            failed.append({"filename": file.filename, "error": str(e)})
            db_log = IngestionLog(
                operation="ingest",
                status="failed",
                filename=file.filename,
                message=str(e),
            )
            db.add(db_log)
            db.commit()

    return IngestionResult(success=success, failed=failed, total=len(success) + len(failed))
