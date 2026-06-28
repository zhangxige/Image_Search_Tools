## Why

Modern flagship phones (iPhone 17 Pro, Samsung S26 Ultra, Vivo X300U, Huawei Mate 80 Pro, etc.) capture photos in HDR (High Dynamic Range) format, but the current image viewer displays them as standard SDR images with no indication of their HDR capability. Users cannot tell which photos are HDR, and the browser is not instructed to use HDR display pipelines, resulting in washed-out or clipped highlights.

## What Changes

- **Backend HDR detection at ingest time**: Analyze EXIF metadata to detect if an image is HDR, storing the result as a boolean + format string
- **HDR badge in gallery**: Show an HDR icon with tooltip on image cards in the gallery grid
- **HDR badge in preview**: Show HDR icon with tooltip (e.g., "Apple HEIC 10-bit", "Samsung HDR10+") in the ImagePreview overlay
- **HDR-aware display**: Use CSS `dynamic-range` media queries and `color-gamut` to enable HDR display in supporting browsers
- **ImageResponse schema extended**: Add `is_hdr: bool` and `hdr_format: Optional[str]` fields

## Capabilities

### New Capabilities
- `hdr-detection`: EXIF-based HDR detection at ingest time, storing is_hdr + hdr_format metadata
- `hdr-display`: Frontend HDR badge (icon + tooltip), browser HDR display pipeline, gallery card integration

### Modified Capabilities
- *(none — no existing formal specs for image-exif or image-preview-overlay)*

## Impact

- **Backend**: New `is_hdr` (Boolean) + `hdr_format` (String) columns on ImageRecord; HDR detection logic in `exif_utils.py`; updated ImageResponse schema; migration for new columns
- **Frontend**: HDR detection logic display in `ImageCard` (via gallery); HDR badge in `ImagePreview.vue`; CSS media queries for `dynamic-range`; tooltip component for HDR format details
