import io
from pathlib import Path
from PIL import Image

EXIF_TAGS = {
    271: "make",
    272: "model",
    33434: "aperture",
    33437: "shutterSpeed",
    34855: "iso",
    37386: "focalLength",
    306: "dateTaken",
}

COLOR_SPACE_TAG = 40961
GAMMA_TAG = 42240
MAKER_NOTE_TAG = 37500

THUMBNAIL_TAGS = {513, 514}

HDR_EXTENSIONS = {".heic", ".heif", ".heics", ".avif"}
APPLE_HDR_INDICATORS = ["portraithdr", "hdrimage", "hdrgainmap"]
SAMSUNG_HDR_INDICATORS = ["hdr10+", "hdr10plus"]
VIVO_HDR_INDICATORS = ["vivohdr", "hdr vivid"]
HUAWEI_HDR_INDICATORS = ["huaweihdr", "hdr"]


def detect_hdr(exif_data: dict | None, mime_type: str | None, file_extension: str = "") -> tuple[bool, str | None]:
    is_hdr = False
    signals = []

    ext = file_extension.lower().strip(".")
    if f".{ext}" in HDR_EXTENSIONS or ext in {"heic", "heif", "avif"}:
        signals.append("format")

    if exif_data is None:
        if signals:
            return True, f"{ext.upper()} HDR" if ext else "HDR"
        return False, None

    raw = exif_data.get("_raw", {})
    if not raw:
        return (True, f"{ext.upper()} HDR") if signals else (False, None)

    color_space = raw.get(COLOR_SPACE_TAG)
    gamma_raw = raw.get(GAMMA_TAG)
    maker_note = raw.get(MAKER_NOTE_TAG)

    if color_space is not None:
        try:
            cs_val = int(color_space) if not isinstance(color_space, int) else color_space
        except (ValueError, TypeError):
            cs_val = None
        if cs_val == 65535:
            signals.append("uncalibrated")
        elif cs_val == 2:
            signals.append("wide_gamut")

    if gamma_raw is not None:
        try:
            gamma_val = _rational_to_float(gamma_raw)
            if gamma_val < 1.8 or gamma_val > 2.6:
                signals.append(f"gamma_{gamma_val:.2f}")
        except Exception:
            pass

    if maker_note is not None:
        mn_str = str(maker_note).lower()
        for ind in APPLE_HDR_INDICATORS:
            if ind in mn_str:
                signals.append("apple_hdr")
                break
        for ind in SAMSUNG_HDR_INDICATORS:
            if ind in mn_str:
                signals.append("samsung_hdr10+")
                break
        for ind in VIVO_HDR_INDICATORS:
            if ind in mn_str:
                signals.append("vivo_hdr")
                break
        for ind in HUAWEI_HDR_INDICATORS:
            if ind in mn_str:
                signals.append("huawei_hdr")
                break

    if not signals:
        return False, None

    is_hdr = True
    if "apple_hdr" in signals:
        label = "Apple HDR"
    elif "samsung_hdr10+" in signals:
        label = "Samsung HDR10+"
    elif "vivo_hdr" in signals:
        label = "Vivo HDR"
    elif "huawei_hdr" in signals:
        label = "Huawei HDR"
    elif "format" in signals:
        label = f"{ext.upper()} HDR"
    elif "uncalibrated" in signals:
        label = "Wide Gamut HDR"
    elif "wide_gamut" in signals:
        label = "Adobe RGB"
    elif gamma_raw is not None:
        label = f"HDR (Gamma {signals[-1]})"
    else:
        label = "HDR"

    return is_hdr, label


def extract_exif(image_path: Path) -> dict | None:
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data is None:
            return None

        result = {}
        raw_exif = {}
        for tag_id, value in exif_data.items():
            if tag_id in THUMBNAIL_TAGS:
                continue
            name = EXIF_TAGS.get(tag_id)
            if name is not None:
                if tag_id == 33434:
                    value = _rational_to_float(value)
                elif tag_id == 33437:
                    value = _rational_to_float(value)
                elif tag_id == 37386:
                    value = _rational_to_float(value)
                result[name] = value
            raw_exif[tag_id] = _sanitize_exif_value(value)

        result["_raw"] = raw_exif

        return result
    except Exception:
        return None


def _sanitize_exif_value(value):
    if isinstance(value, (bytes, bytearray)):
        return value.hex()[:200]
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return _rational_to_float(value)
    if isinstance(value, tuple):
        return tuple(_sanitize_exif_value(v) for v in value)
    if isinstance(value, float):
        return round(value, 4)
    return value


def _rational_to_float(value):
    if isinstance(value, tuple):
        if len(value) == 2 and value[1] != 0:
            return round(value[0] / value[1], 2)
        return float(value[0]) if value else 0.0
    return float(value) if value else 0.0


_HEIF_EXTS = {".heic", ".heif", ".heics", ".avif"}


def heif_to_pil(contents: bytes) -> Image.Image:
    """Convert HEIF/HEIC/AVIF bytes to a PIL Image. Handles multiple pillow-heif API versions."""
    from pillow_heif import open_heif
    heif_file = open_heif(io.BytesIO(contents))
    if hasattr(heif_file, "to_pil_image"):
        return heif_file.to_pil_image()
    if hasattr(heif_file, "to_image"):
        return heif_file.to_image()
    try:
        primary = heif_file[0]
    except (TypeError, IndexError):
        primary = heif_file
    if hasattr(primary, "to_rgb"):
        import numpy as np
        return Image.fromarray(primary.to_rgb())
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".heic", delete=False)
    try:
        tmp.write(contents)
        tmp.close()
        img = Image.open(tmp.name)
        img.load()
        return img
    finally:
        os.unlink(tmp.name)


def heif_to_pil_with_exif(contents: bytes) -> tuple[Image.Image, bytes | None]:
    """Like heif_to_pil() but also returns raw EXIF bytes from the HEIF container."""
    from pillow_heif import open_heif
    heif_file = open_heif(io.BytesIO(contents))
    info = heif_file.info
    exif_bytes = info.exif if hasattr(info, "exif") else (info.get("exif") if isinstance(info, dict) else None)
    return heif_to_pil(contents), exif_bytes


def open_image(contents: bytes, filename: str) -> Image.Image:
    """Open any image (including HEIC/HEIF/AVIF) from bytes and return RGB PIL Image."""
    ext = Path(filename).suffix.lower()
    if ext in _HEIF_EXTS:
        return heif_to_pil(contents).convert("RGB")
    return Image.open(io.BytesIO(contents)).convert("RGB")
