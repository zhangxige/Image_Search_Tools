import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Text, JSON, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, unique=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True, default="")
    exif_data = Column(JSON, nullable=True)
    is_hdr = Column(Boolean, default=False, index=True)
    hdr_format = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    features = relationship("FeatureVector", back_populates="image", cascade="all, delete-orphan")
    logs = relationship("IngestionLog", back_populates="image", cascade="all, delete-orphan")


class FeatureVector(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    vector = Column(LargeBinary, nullable=False)
    dimension = Column(Integer, default=2048)
    model_name = Column(String(50), nullable=False, default="xception")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("image_id", "model_name", name="uq_image_model"),
    )

    image = relationship("ImageRecord", back_populates="features")


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    filename = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    image = relationship("ImageRecord", back_populates="logs")
