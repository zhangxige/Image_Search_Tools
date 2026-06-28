import pickle
import threading
import numpy as np
import faiss
from typing import Optional

from app.config import VECTOR_DIM, FAISS_INDEX_PATH, TOP_K

_index: Optional[faiss.Index] = None
_id_to_index: dict = {}
_index_to_id: dict = {}
_next_id: int = 0
_lock = threading.Lock()


def get_index() -> faiss.Index:
    global _index
    if _index is None:
        _index = faiss.IndexFlatIP(VECTOR_DIM)
    return _index


def build_index(all_ids: list, all_vectors: np.ndarray):
    global _index, _id_to_index, _index_to_id, _next_id
    with _lock:
        _index = faiss.IndexFlatIP(VECTOR_DIM)
        _id_to_index = {}
        _index_to_id = {}
        _next_id = 0

        if len(all_vectors) > 0:
            _index.add(all_vectors)
            for i, img_id in enumerate(all_ids):
                _id_to_index[img_id] = i
                _index_to_id[i] = img_id
            _next_id = len(all_vectors)

    save_index()


def add_to_index(image_id: int, vector: np.ndarray):
    global _next_id
    with _lock:
        idx = get_index()
        idx.add(vector.reshape(1, -1))
        _id_to_index[image_id] = _next_id
        _index_to_id[_next_id] = image_id
        _next_id += 1
    save_index()


def search(vector: np.ndarray, k: int = TOP_K) -> list:
    idx = get_index()
    if idx.ntotal == 0:
        return []
    k = min(k, idx.ntotal)
    distances, indices = idx.search(vector.reshape(1, -1), k)
    results = []
    for dist, faiss_idx in zip(distances[0], indices[0]):
        if faiss_idx == -1:
            continue
        image_id = _index_to_id.get(int(faiss_idx))
        if image_id is not None:
            results.append((image_id, float(dist)))
    return results


def save_index():
    idx = get_index()
    faiss.write_index(idx, str(FAISS_INDEX_PATH))
    meta = {
        "id_to_index": _id_to_index,
        "index_to_id": _index_to_id,
        "next_id": _next_id,
    }
    meta_path = FAISS_INDEX_PATH.with_suffix(".meta.pkl")
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)


def rebuild_from_db(db_session) -> int:
    from app.models import ImageRecord, FeatureVector

    records = db_session.query(ImageRecord, FeatureVector).join(FeatureVector).all()
    if records:
        ids = []
        vectors = []
        for rec, feat in records:
            ids.append(rec.id)
            vectors.append(np.frombuffer(feat.vector, dtype=np.float32))
        build_index(ids, np.array(vectors))
    else:
        build_index([], np.array([]).reshape(0, VECTOR_DIM))
    return len(records)


def load_index():
    global _index, _id_to_index, _index_to_id, _next_id
    if FAISS_INDEX_PATH.exists():
        _index = faiss.read_index(str(FAISS_INDEX_PATH))
        meta_path = FAISS_INDEX_PATH.with_suffix(".meta.pkl")
        if meta_path.exists():
            with open(meta_path, "rb") as f:
                meta = pickle.load(f)
            _id_to_index = meta["id_to_index"]
            _index_to_id = meta["index_to_id"]
            _next_id = meta["next_id"]
    else:
        _index = faiss.IndexFlatIP(VECTOR_DIM)
        _id_to_index = {}
        _index_to_id = {}
        _next_id = 0
