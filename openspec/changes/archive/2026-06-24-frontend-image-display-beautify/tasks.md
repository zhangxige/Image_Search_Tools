## 1. Database Migration

- [x] 1.1 Add `exif_data` JSON nullable column to `ImageRecord` model via Alembic or raw SQL migration
- [x] 1.2 Create migration script (`_migrate()`) that ALTER TABLE ADD COLUMN IF NOT EXISTS

## 2. Backend EXIF Extraction

- [x] 2.1 Create `exif_utils.py` with EXIF tag mapping (numeric IDs to human-readable keys)
- [x] 2.2 Implement `extract_exif(image_path: Path) -> dict | None` using Pillow `_getexif()`
- [x] 2.3 Strip embedded thumbnail tags (513, 514) from extracted data
- [x] 2.4 Integrate EXIF extraction into ingest router (call after PIL open, store in `exif_data`)

## 3. Backend EXIF API Endpoint

- [x] 3.1 Create `GET /api/images/{id}/exif` endpoint in a new or existing router
- [x] 3.2 Implement on-the-fly extraction for legacy images with null `exif_data`
- [x] 3.3 Add proper 404 handling and error responses
- [x] 3.4 Add EXIF schema to `schemas.py` (`ExifResponse` with `hasExif`, optional metadata fields)
- [x] 3.5 Register the new router in `main.py`

## 4. Frontend EXIF Panel Component

- [x] 4.1 Create `ExifPanel.vue` with slide-in drawer layout (right side, max-width 320px)
- [x] 4.2 Group EXIF fields into sections: Camera (make, model), Settings (aperture, shutter, ISO, focal length), File (date taken, dimensions)
- [x] 4.3 Fetch EXIF data from `GET /api/images/{id}/exif` when preview opens
- [x] 4.4 Show "No EXIF data available" when `hasExif` is false
- [x] 4.5 Add slide-in/out CSS transition animation

## 5. Frontend ImagePreview Overlay Redesign

- [x] 5.1 Rewrite `ImagePreview.vue` as full-viewport overlay with frosted glass background
- [x] 5.2 Implement frosted glass effect: duplicate image as CSS `background-image`, scaled up and blurred with `backdrop-filter: blur(20px)`
- [x] 5.3 Add info (i) toggle button to show/hide EXIF panel
- [x] 5.4 Integrate `ExifPanel.vue` component into the overlay
- [x] 5.5 Preserve existing tag editing functionality
- [x] 5.6 Ensure keyboard navigation (ArrowLeft, ArrowRight, Escape) still works
- [x] 5.7 Add responsive behavior for narrow viewports (EXIF panel collapses or overlays)

## 6. Verification

- [ ] 6.1 Run backend tests (`cd backend && uv run pytest tests/`) — confirm no regressions
- [ ] 6.2 Run frontend tests (`cd frontend && npm run test`) — confirm no regressions
- [ ] 6.3 Manually verify EXIF display with test images containing known EXIF data
- [ ] 6.4 Verify frosted glass effect renders correctly in Chrome and Firefox
- [ ] 6.5 Verify graceful handling of images without EXIF data
- [ ] 6.6 Verify legacy images (pre-migration) show EXIF via on-the-fly extraction
