import pytest
import numpy as np
from app.feature_extractor import (
    get_available_models,
    get_model_dim,
    get_model_input_size,
    MODEL_REGISTRY,
    _transformers_available,
)


class TestModelRegistry:
    def test_available_models(self):
        models = get_available_models()
        assert "xception" in models
        assert "resnet50" in models
        if _transformers_available:
            assert "clip" in models

    def test_model_dims(self):
        assert get_model_dim("xception") == 2048
        assert get_model_dim("resnet50") == 2048
        if _transformers_available:
            assert get_model_dim("clip") == 512

    def test_model_input_sizes(self):
        assert get_model_input_size("xception") == 299
        assert get_model_input_size("resnet50") == 224
        if _transformers_available:
            assert get_model_input_size("clip") == 224

    def test_unknown_model_raises_key_error(self):
        with pytest.raises(KeyError):
            get_model_dim("unknown_model")

    def test_registry_entries_have_required_keys(self):
        for name in get_available_models():
            entry = MODEL_REGISTRY[name]
            assert "name" in entry
            assert "dim" in entry
            assert "input_size" in entry
            assert "load_fn" in entry
            assert "extract_fn" in entry
            assert "_model" in entry
            assert "_lock" in entry


class TestPerModelFAISS:
    def test_separate_indexes_per_model(self):
        from app.faiss_manager import build_index, get_index

        build_index("xception", [], np.array([]).reshape(0, 2048))
        build_index("resnet50", [], np.array([]).reshape(0, 2048))

        assert get_index("xception").d == 2048
        assert get_index("resnet50").d == 2048

    def test_rebuild_filters_by_model_name(self, db_session):
        from app.models import ImageRecord, FeatureVector
        from app.faiss_manager import rebuild_from_db, get_index

        img = ImageRecord(filename="test.jpg", original_filename="test.jpg")
        db_session.add(img)
        db_session.flush()

        vec_x = np.zeros(2048, dtype=np.float32)
        vec_x[0] = 1.0
        db_session.add(FeatureVector(
            image_id=img.id, vector=vec_x.tobytes(), dimension=2048, model_name="xception"
        ))
        db_session.commit()

        n = rebuild_from_db(db_session, "xception")
        assert n == 1
        assert get_index("xception").ntotal == 1

        n = rebuild_from_db(db_session, "resnet50")
        assert n == 0
        assert get_index("resnet50").ntotal == 0

    def test_search_in_correct_model(self):
        from app.faiss_manager import build_index, add_to_index, search

        build_index("xception", [], np.array([]).reshape(0, 2048))

        vec = np.zeros(2048, dtype=np.float32)
        vec[0] = 1.0
        add_to_index("xception", 1, vec)

        results = search(vec, k=1, model_name="xception")
        assert len(results) == 1
        assert results[0][0] == 1


class TestAPIModels:
    def test_get_models_endpoint(self, client):
        resp = client.get("/api/models")
        assert resp.status_code == 200
        models = resp.json()
        assert "xception" in models
        assert "resnet50" in models

    def test_search_with_model_param(self, client, sample_image):
        from app.faiss_manager import build_index
        build_index("xception", [], np.array([]).reshape(0, 2048))

        _ingest_image(client)

        sample_image.seek(0)
        resp = client.post(
            "/api/search?model=xception",
            files={"files": ("query.png", sample_image, "image/png")},
            data={"top_k": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["model"] == "xception"

    def test_search_default_model(self, client, sample_image):
        from app.faiss_manager import build_index
        build_index("xception", [], np.array([]).reshape(0, 2048))

        _ingest_image(client)

        sample_image.seek(0)
        resp = client.post(
            "/api/search",
            files={"files": ("query.png", sample_image, "image/png")},
            data={"top_k": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    def test_ingest_with_model_param(self, client, sample_image):
        from app.faiss_manager import build_index
        build_index("xception", [], np.array([]).reshape(0, 2048))

        sample_image.seek(0)
        resp = client.post(
            "/api/ingest?model=xception",
            files={"files": ("test.png", sample_image, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    def test_ingest_all_models_default(self, client, sample_image):
        from app.faiss_manager import build_index
        for m in get_available_models():
            dim = get_model_dim(m)
            build_index(m, [], np.array([]).reshape(0, dim))

        sample_image.seek(0)
        resp = client.post(
            "/api/ingest",
            files={"files": ("test.png", sample_image, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1


def _ingest_image(client, name="seed.png"):
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (299, 299), color="red").save(buf, format="PNG")
    buf.seek(0)
    resp = client.post("/api/ingest", files={"files": (name, buf, "image/png")})
    return resp.json()
