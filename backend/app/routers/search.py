from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImageRecord
from app.schemas import SearchResponse, SearchResult, ImageResponse
from app.feature_extractor import extract_feature
from app.faiss_manager import search as faiss_search
from app.config import TOP_K
from app.exif_utils import open_image

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search_images(
    files: list[UploadFile] = File(...),
    top_k: int = Form(TOP_K),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    all_distances = {}

    for file in files:
        contents = file.file.read()
        image = open_image(contents, file.filename)
        feature = extract_feature(image)
        results = faiss_search(feature, top_k)

        for image_id, distance in results:
            if image_id not in all_distances:
                all_distances[image_id] = 0.0
            all_distances[image_id] += distance

    num_queries = len(files)
    if num_queries > 1:
        for img_id in all_distances:
            all_distances[img_id] /= num_queries

    sorted_results = sorted(all_distances.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for image_id, distance in sorted_results:
        record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
        if record:
            results.append(SearchResult(
                image=ImageResponse.model_validate(record),
                distance=distance,
            ))

    return SearchResponse(results=results)
