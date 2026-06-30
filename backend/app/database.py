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
    if "features" in inspector.get_table_names():
        feat_columns = {c["name"] for c in inspector.get_columns("features")}
        feat_constraints = {tuple(c["column_names"]) for c in inspector.get_unique_constraints("features")}
        with engine.connect() as conn:
            if "model_name" not in feat_columns:
                conn.execute(text("ALTER TABLE features ADD COLUMN model_name VARCHAR(50) NOT NULL DEFAULT 'xception'"))
            if ("image_id",) in feat_constraints and ("image_id", "model_name") not in feat_constraints:
                conn.execute(text("""
                    CREATE TABLE features_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER NOT NULL REFERENCES images(id),
                        vector BLOB NOT NULL,
                        dimension INTEGER DEFAULT 2048,
                        model_name VARCHAR(50) NOT NULL DEFAULT 'xception',
                        created_at DATETIME,
                        UNIQUE(image_id, model_name)
                    )
                """))
                conn.execute(text("INSERT INTO features_new (id, image_id, vector, dimension, model_name, created_at) SELECT id, image_id, vector, dimension, model_name, created_at FROM features"))
                conn.execute(text("DROP TABLE features"))
                conn.execute(text("ALTER TABLE features_new RENAME TO features"))
                import logging
                logging.getLogger(__name__).info("Migrated features UNIQUE(image_id) → UNIQUE(image_id, model_name)")
            conn.commit()
    import logging
    logging.getLogger(__name__).info("Database migration complete")
