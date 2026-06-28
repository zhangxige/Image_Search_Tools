import sys
from pathlib import Path
from unittest.mock import patch
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io

import app.database

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TEST_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

app.database.engine = TEST_ENGINE
app.database.SessionLocal = TEST_SESSION_LOCAL

from app.database import Base, get_db, init_db
from app.main import app

# Let the startup run once at import time to initialize tables on TEST_ENGINE


def _make_mock_extract():
    def mock_extract(image):
        rng = np.random.RandomState(42)
        vec = rng.randn(2048).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm
    return mock_extract


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TEST_SESSION_LOCAL()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def mock_feature_extractor():
    mock_fn = _make_mock_extract()
    targets = [
        "app.feature_extractor.extract_feature",
        "app.routers.ingest.extract_feature",
        "app.routers.search.extract_feature",
    ]
    patchers = [patch(t, mock_fn) for t in targets]
    for p in patchers:
        p.start()
    yield
    for p in patchers:
        p.stop()


@pytest.fixture()
def client(db_session, mock_feature_extractor):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    from app.faiss_manager import build_index
    build_index([], np.array([]).reshape(0, 2048))

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def sample_image():
    img = Image.new("RGB", (299, 299), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@pytest.fixture()
def sample_image_file(sample_image):
    return io.BytesIO(sample_image.getvalue())
