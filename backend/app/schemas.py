from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    tags: str = ""
    is_hdr: bool = False
    hdr_format: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImageUpdate(BaseModel):
    tags: Optional[str] = None


class SearchResult(BaseModel):
    image: ImageResponse
    distance: float


class SearchResponse(BaseModel):
    results: List[SearchResult]


class IngestionLogResponse(BaseModel):
    id: int
    operation: str
    status: str
    image_id: Optional[int] = None
    filename: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IngestionResult(BaseModel):
    success: List[ImageResponse]
    failed: List[dict]
    total: int


class ExifResponse(BaseModel):
    hasExif: bool
    make: Optional[str] = None
    model: Optional[str] = None
    aperture: Optional[float] = None
    shutterSpeed: Optional[float] = None
    iso: Optional[int] = None
    focalLength: Optional[float] = None
    dateTaken: Optional[str] = None
