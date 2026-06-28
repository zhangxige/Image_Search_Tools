import numpy as np
import faiss

from app.faiss_manager import (
    get_index, build_index, add_to_index, search,
)


class TestBuildIndex:
    def test_build_with_correct_dimension(self):
        build_index([], np.array([]).reshape(0, 2048))
        idx = get_index()
        assert idx.d == 2048
        assert isinstance(idx, faiss.IndexFlatIP)

    def test_build_with_vectors(self):
        ids = [1, 2, 3]
        vectors = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ], dtype=np.float32)
        # Pad to 2048 dim
        padded = np.zeros((3, 2048), dtype=np.float32)
        padded[:, :3] = vectors

        build_index(ids, padded)
        assert get_index().ntotal == 3


class TestAddToIndex:
    def test_add_and_search_returns_it(self):
        build_index([], np.array([]).reshape(0, 2048))
        vec = np.zeros(2048, dtype=np.float32)
        vec[0] = 1.0
        add_to_index(42, vec)

        results = search(vec, k=1)
        assert len(results) == 1
        assert results[0][0] == 42
        assert results[0][1] > 0.9

    def test_add_multiple_and_search(self):
        build_index([], np.array([]).reshape(0, 2048))
        for i in range(5):
            v = np.zeros(2048, dtype=np.float32)
            v[i] = 1.0
            add_to_index(i, v)

        query = np.zeros(2048, dtype=np.float32)
        query[0] = 1.0
        results = search(query, k=3)
        assert len(results) == 3
        assert results[0][0] == 0


class TestSearch:
    def test_empty_index_returns_empty(self):
        build_index([], np.array([]).reshape(0, 2048))
        vec = np.random.randn(2048).astype(np.float32)
        results = search(vec, k=5)
        assert results == []

    def test_top_k_respected(self):
        build_index([], np.array([]).reshape(0, 2048))
        for i in range(10):
            v = np.random.randn(2048).astype(np.float32)
            norm = np.linalg.norm(v)
            add_to_index(i, v / norm)

        query = np.random.randn(2048).astype(np.float32)
        norm = np.linalg.norm(query)
        results = search(query / norm, k=4)
        assert len(results) == 4

    def test_distance_is_inner_product(self):
        build_index([], np.array([]).reshape(0, 2048))
        vec = np.zeros(2048, dtype=np.float32)
        vec[0] = 1.0
        add_to_index(1, vec)
        add_to_index(2, -vec)

        query = np.zeros(2048, dtype=np.float32)
        query[0] = 1.0
        results = search(query, k=2)
        assert len(results) == 2
        assert results[0][1] >= results[1][1]


class TestRebuildFromDB:
    def test_rebuild_from_db(self, db_session):
        from app.models import ImageRecord, FeatureVector
        import io
        from PIL import Image

        # Manually seed DB with records and feature vectors
        for i in range(3):
            rec = ImageRecord(
                filename=f"rebuild_{i}.jpg",
                original_filename=f"rebuild_{i}.jpg",
            )
            db_session.add(rec)
            db_session.flush()

            v = np.zeros(2048, dtype=np.float32)
            v[i] = 1.0
            feat = FeatureVector(image_id=rec.id, vector=v.tobytes())
            db_session.add(feat)
        db_session.commit()

        from app.faiss_manager import rebuild_from_db
        n = rebuild_from_db(db_session)
        assert n == 3
        assert get_index().ntotal == 3
