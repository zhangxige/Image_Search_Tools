import pickle
import threading
import numpy as np
import faiss
from pathlib import Path
from typing import Optional

from app.config import DATA_DIR, TOP_K

_models: dict[str, dict] = {}


def _state(model_name: str) -> dict:
    if model_name not in _models:
        _models[model_name] = {
            "index": None,
            "id_to_index": {},
            "index_to_id": {},
            "next_id": 0,
            "lock": threading.Lock(),
        }
    return _models[model_name]


def _index_path(model_name: str) -> Path:
    return DATA_DIR / f"faiss_{model_name}.index"


def _meta_path(model_name: str) -> Path:
    return DATA_DIR / f"faiss_{model_name}.meta.pkl"


def get_index(model_name: str) -> faiss.Index:
    from app.feature_extractor import get_model_dim
    s = _state(model_name)
    if s["index"] is None:
        s["index"] = faiss.IndexFlatIP(get_model_dim(model_name))
    return s["index"]


def build_index(model_name: str, all_ids: list, all_vectors: np.ndarray):
    s = _state(model_name)
    with s["lock"]:
        dim = all_vectors.shape[1] if len(all_vectors) > 0 else 1
        s["index"] = faiss.IndexFlatIP(dim)
        s["id_to_index"] = {}
        s["index_to_id"] = {}
        s["next_id"] = 0
        if len(all_vectors) > 0:
            s["index"].add(all_vectors)
            for i, img_id in enumerate(all_ids):
                s["id_to_index"][img_id] = i
                s["index_to_id"][i] = img_id
            s["next_id"] = len(all_vectors)
    save_index(model_name)


def add_to_index(model_name: str, image_id: int, vector: np.ndarray):
    s = _state(model_name)
    with s["lock"]:
        idx = get_index(model_name)
        idx.add(vector.reshape(1, -1))
        s["id_to_index"][image_id] = s["next_id"]
        s["index_to_id"][s["next_id"]] = image_id
        s["next_id"] += 1
    save_index(model_name)


def search(vector: np.ndarray, k: int = TOP_K, model_name: str = "xception") -> list:
    s = _state(model_name)
    if s["index"] is None:
        load_index(model_name)
    idx = get_index(model_name)
    if idx.ntotal == 0:
        return []
    k = min(k, idx.ntotal)
    distances, indices = idx.search(vector.reshape(1, -1), k)
    results = []
    for dist, faiss_idx in zip(distances[0], indices[0]):
        if faiss_idx == -1:
            continue
        image_id = s["index_to_id"].get(int(faiss_idx))
        if image_id is not None:
            results.append((image_id, float(dist)))
    return results


def save_index(model_name: str):
    s = _state(model_name)
    idx = get_index(model_name)
    faiss.write_index(idx, str(_index_path(model_name)))
    meta = {
        "id_to_index": s["id_to_index"],
        "index_to_id": s["index_to_id"],
        "next_id": s["next_id"],
    }
    with open(_meta_path(model_name), "wb") as f:
        pickle.dump(meta, f)


def rebuild_from_db(db_session, model_name: str = "xception") -> int:
    from app.models import ImageRecord, FeatureVector
    from app.feature_extractor import get_model_dim

    records = (
        db_session.query(ImageRecord, FeatureVector)
        .join(FeatureVector)
        .filter(FeatureVector.model_name == model_name)
        .all()
    )
    dim = get_model_dim(model_name)
    if records:
        ids = []
        vectors = []
        for rec, feat in records:
            ids.append(rec.id)
            vectors.append(np.frombuffer(feat.vector, dtype=np.float32))
        build_index(model_name, ids, np.array(vectors))
    else:
        build_index(model_name, [], np.array([]).reshape(0, dim))
    return len(records)


def load_index(model_name: str):
    s = _state(model_name)
    path = _index_path(model_name)
    if path.exists():
        s["index"] = faiss.read_index(str(path))
        meta_path = _meta_path(model_name)
        if meta_path.exists():
            with open(meta_path, "rb") as f:
                meta = pickle.load(f)
            s["id_to_index"] = meta["id_to_index"]
            s["index_to_id"] = meta["index_to_id"]
            s["next_id"] = meta["next_id"]
    else:
        from app.feature_extractor import get_model_dim
        s["index"] = faiss.IndexFlatIP(get_model_dim(model_name))
        s["id_to_index"] = {}
        s["index_to_id"] = {}
        s["next_id"] = 0


def rename_legacy_index():
    """Rename faiss.index → faiss_xception.index on first startup after migration."""
    legacy = DATA_DIR / "faiss.index"
    legacy_meta = DATA_DIR / "faiss.meta.pkl"
    target = _index_path("xception")
    target_meta = _meta_path("xception")
    if legacy.exists() and not target.exists():
        legacy.rename(target)
        if legacy_meta.exists():
            legacy_meta.rename(target_meta)


def get_all_model_names() -> list[str]:
    from app.feature_extractor import get_available_models
    return get_available_models()
