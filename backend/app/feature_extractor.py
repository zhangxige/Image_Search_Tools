import threading
import timm
import torch
import torchvision.transforms as transforms
import numpy as np
from PIL import Image

_device = None


def get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


# ── Registry ──────────────────────────────────────────────────────────────

MODEL_REGISTRY = {}


def register_model(name, dim, input_size, load_fn, extract_fn):
    MODEL_REGISTRY[name] = {
        "name": name,
        "dim": dim,
        "input_size": input_size,
        "load_fn": load_fn,
        "extract_fn": extract_fn,
        "_model": None,
        "_lock": threading.Lock(),
    }


class ModelLoadError(RuntimeError):
    pass


def get_model(name, strict=True):
    entry = MODEL_REGISTRY[name]
    if entry["_model"] is None:
        with entry["_lock"]:
            if entry["_model"] is None:
                try:
                    entry["_model"] = entry["load_fn"]()
                except Exception as e:
                    del MODEL_REGISTRY[name]
                    msg = f"Failed to load model '{name}': {e}. Model removed from registry."
                    if strict:
                        raise ModelLoadError(msg) from e
                    import logging
                    logging.getLogger(__name__).warning(msg)
                    return None
    return entry["_model"]


def get_model_dim(name):
    return MODEL_REGISTRY[name]["dim"]


def get_model_input_size(name):
    return MODEL_REGISTRY[name]["input_size"]


def get_available_models():
    return list(MODEL_REGISTRY.keys())


# ── Xception (timm) ───────────────────────────────────────────────────────

def _load_xception():
    base = timm.create_model("legacy_xception", pretrained=True)
    base.reset_classifier(0)
    return base.eval().to(get_device())


def _extract_xception(image, model):
    transform = transforms.Compose([
        transforms.Resize((299, 299)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = transform(image.convert("RGB")).unsqueeze(0).to(get_device())
    with torch.no_grad():
        feature = model(img).squeeze().cpu().numpy()
    norm = np.linalg.norm(feature)
    if norm > 0:
        feature = feature / norm
    return feature.astype(np.float32)


register_model("xception", 2048, 299, _load_xception, _extract_xception)


# ── ResNet50 (timm) ───────────────────────────────────────────────────────

def _load_resnet50():
    base = timm.create_model("resnet50", pretrained=True)
    base.reset_classifier(0)
    return base.eval().to(get_device())


def _extract_resnet50(image, model):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = transform(image.convert("RGB")).unsqueeze(0).to(get_device())
    with torch.no_grad():
        feature = model(img).squeeze().cpu().numpy()
    norm = np.linalg.norm(feature)
    if norm > 0:
        feature = feature / norm
    return feature.astype(np.float32)


register_model("resnet50", 2048, 224, _load_resnet50, _extract_resnet50)


# ── CLIP (transformers) — optional ───────────────────────────────────────

try:
    from transformers import CLIPModel, CLIPProcessor

    _transformers_available = True
except ImportError:
    _transformers_available = False


def _load_clip():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return (model.eval().to(get_device()), processor)


def _extract_clip(image, model_and_processor):
    model, processor = model_and_processor
    inputs = processor(images=image.convert("RGB"), return_tensors="pt").to(get_device())
    with torch.no_grad():
        feature = model.get_image_features(**inputs).squeeze().cpu().numpy()
    norm = np.linalg.norm(feature)
    if norm > 0:
        feature = feature / norm
    return feature.astype(np.float32)


if _transformers_available:
    register_model("clip", 512, 224, _load_clip, _extract_clip)


# ── Backward-compatible aliases ──────────────────────────────────────────

def extract_feature(image: Image.Image, model_name: str = "xception") -> np.ndarray:
    entry = MODEL_REGISTRY[model_name]
    model = get_model(model_name)
    return entry["extract_fn"](image, model)


def extract_feature_from_path(path: str, model_name: str = "xception") -> np.ndarray:
    image = Image.open(path).convert("RGB")
    return extract_feature(image, model_name)
