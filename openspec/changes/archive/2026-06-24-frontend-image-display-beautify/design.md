## Context

The current `ImagePreview.vue` is a simple centered modal with a dark overlay, prev/next buttons, and an inline tag editor. It lacks EXIF metadata display and the viewing experience is minimal. The backend stores image dimensions/file size but does not extract or expose EXIF camera metadata (make, model, aperture, shutter speed, ISO, focal length, date taken).

## Goals / Non-Goals

**Goals:**
- Extract and store EXIF metadata from uploaded images at ingest time
- Expose EXIF data via a new API endpoint
- Redesign `ImagePreview.vue` as a full-screen overlay with frosted glass (毛玻璃) backdrop
- Add an EXIF metadata panel as a slide-in sidebar within the preview
- Support prev/next navigation within the overlay
- Preserve existing tag editing capability

**Non-Goals:**
- EXIF editing or writing — read-only display
- Client-side EXIF parsing — all extraction happens on the backend
- Touch/gesture support beyond keyboard navigation
- Video file EXIF support — images only

## Decisions

1. **EXIF storage: JSON column on ImageRecord** — Add a nullable `exif_data` JSON column. Extracted at ingest time via Pillow (`_getexif()`). This avoids a separate table and keeps reads fast. On-demand extraction endpoint also available for legacy images.

2. **Backend: Pillow for EXIF extraction** — Already a dependency; `PIL.Image._getexif()` returns a dict of EXIF tags. Map numeric tag IDs to human-readable names (e.g., 271 → "Make", 272 → "Model", 33434 → "ApertureValue").

3. **Frontend: Vue Teleport overlay** — Keep using `<Teleport to="body">` but switch from a centered card to a full-viewport layout: image fills most of the screen with the frosted glass background, EXIF panel slides in from the right.

4. **Frosted glass effect** — Use `backdrop-filter: blur(20px)` on the overlay background, combined with a semi-transparent layer. The image itself is centered with `object-fit: contain`. The blurred background uses a duplicate image as CSS `background-image` (scaled up + blurred) to create the true iOS 毛玻璃 look.

5. **EXIF panel: slide-in drawer** — A right-side panel (`max-width: 320px`) with grouped metadata rows (Camera, Settings, File). Opens via a info button, closed by default. Slides in with CSS transition.

6. **EXIF API: on-demand extraction** — New endpoint `GET /api/images/{id}/exif` reads from the stored `exif_data` column. If null (legacy images), extracts on-the-fly from the stored file and caches back to DB.

## Risks / Trade-offs

- **Risk:** `PIL.Image._getexif()` is undocumented and may return None for images without EXIF. **Mitigation:** Handle gracefully — return empty object with `{"hasExif": false}`.
- **Risk:** Large EXIF data (e.g., embedded thumbnails). **Mitigation:** Strip thumbnail tags (513, 514) during extraction; store only metadata tags.
- **Risk:** `backdrop-filter: blur()` has varying browser support. **Mitigation:** Use `background: rgba(0,0,0,0.7)` as fallback; the blur is enhancement only.
- **Trade-off:** Storing EXIF in JSON column means no querying on EXIF fields. Acceptable — EXIF is for display only, not search/filter.

## Open Questions

- Should the EXIF panel be auto-open or triggered by a button? → Button-triggered (info icon) to keep the clean viewing experience.
- Should we add a thumbnail strip at the bottom for multi-image navigation? → Future enhancement; current prev/next arrows suffice.
