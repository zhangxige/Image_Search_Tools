import timm
import torch
import torchvision.transforms as transforms
import numpy as np
from PIL import Image

from app.config import IMG_SIZE, VECTOR_DIM

_device = None
_model = None
_transform = None


def get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def get_transform():
    global _transform
    if _transform is None:
        _transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    return _transform


def get_model():
    global _model
    if _model is not None:
        return _model

    base = timm.create_model("xception", pretrained=True)
    base.reset_classifier(0)
    _model = base.eval().to(get_device())
    return _model


def extract_feature(image: Image.Image) -> np.ndarray:
    transform = get_transform()
    img = transform(image.convert("RGB")).unsqueeze(0).to(get_device())

    model = get_model()
    with torch.no_grad():
        feature = model(img).squeeze().cpu().numpy()

    norm = np.linalg.norm(feature)
    if norm > 0:
        feature = feature / norm

    return feature.astype(np.float32)


def extract_feature_from_path(path: str) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    return extract_feature(image)
