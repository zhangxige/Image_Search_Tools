from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("images")}
    with engine.connect() as conn:
        if "tags" not in columns:
            conn.execute(text("ALTER TABLE images ADD COLUMN tags TEXT DEFAULT ''"))
            conn.commit()
        if "exif_data" not in columns:
            conn.execute(text("ALTER TABLE images ADD COLUMN exif_data JSON"))
            conn.commit()
        if "is_hdr" not in columns:
            conn.execute(text("ALTER TABLE images ADD COLUMN is_hdr BOOLEAN DEFAULT 0"))
            conn.commit()
        if "hdr_format" not in columns:
            conn.execute(text("ALTER TABLE images ADD COLUMN hdr_format VARCHAR(50)"))
            conn.commit()
    import logging
    logging.getLogger(__name__).info("Database migration complete")
