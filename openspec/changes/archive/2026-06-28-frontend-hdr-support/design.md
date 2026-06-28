## Context

The `exif_utils.py` currently extracts camera metadata (make, model, aperture, etc.) but does not detect HDR content. The backend stores EXIF in a JSON column (`exif_data`). The frontend gallery and preview show image metadata but have no HDR indicator. The `ImagePreview.vue` was recently rewritten with a frosted glass overlay.

Modern phones produce HDR images that need:
- Detection at ingest time from EXIF tags (color space, gamma, maker notes)
- A visual badge so users know which images are HDR
- CSS-level HDR display hints for supporting browsers (`color-gamut`, `dynamic-range`)

## Goals / Non-Goals

**Goals:**
- Detect HDR images at ingest time by analyzing EXIF metadata
- Store `is_hdr: bool` and `hdr_format: str | null` on `ImageRecord`
- Show HDR icon + tooltip on gallery cards and in the image preview
- Add CSS `dynamic-range` and `color-gamut` media queries for HDR-aware rendering

**Non-Goals:**
- Server-side HDR-to-SDR tone mapping — display original HDR data
- Editing HDR metadata — detection only
- Full HDR video support — still images only

## Decisions

1. **HDR detection logic in `exif_utils.py`** — Add a `detect_hdr(exif_data: dict, mime_type: str) -> tuple[bool, str | None]` function. Uses multiple EXIF heuristics: ColorSpace tag (40961), Gamma tag (42240), MakerNotes HDR flags, file format (HEIC/AVIF). Returns `(is_hdr, format_label)`.

2. **Storage: two new columns** — `is_hdr: Boolean` (indexed, default false) and `hdr_format: String(50)` (nullable) on `ImageRecord`. Separate from `exif_data` JSON for fast querying.

3. **ImageResponse schema extended** — Add `is_hdr: bool = False` and `hdr_format: Optional[str] = None` so the frontend gets HDR info in every image list response.

4. **Frontend HDR badge** — A reusable `<HdrBadge>` component showing an HDR icon with tooltip. Used in gallery card `image-info` section and `ImagePreview` top-bar. Tooltip displays `hdr_format` text.

5. **CSS HDR display** — Use `@media (dynamic-range: high)` to apply `image-rendering: auto` and wide-gamut color hints. Add `color-gamut: p3` as progressive enhancement.

## Risks / Trade-offs

- **Risk:** EXIF-based HDR detection is heuristic — may miss some HDR images or falsely flag SDR images. **Mitigation:** Use multiple indicators (color space, gamma, file format, maker notes) and document known patterns per phone brand.
- **Risk:** `dynamic-range` CSS media query has limited browser support (Safari 17+, Chrome 120+). **Mitigation:** HDR badge and tooltip work regardless of CSS support; HDR display is progressive enhancement only.
- **Risk:** New columns require DB migration. **Mitigation:** Use same `_migrate()` pattern with IF NOT EXISTS; default values for existing rows.
