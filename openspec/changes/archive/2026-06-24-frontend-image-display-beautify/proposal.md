## Why

Image preview is currently a basic modal — it shows the image in a plain dialog with no contextual information and no visual polish. Users cannot see camera settings, date taken, or other EXIF metadata, and the viewing experience lacks the polished aesthetic users expect from modern image viewers. This change brings the frontend image preview up to modern standards with rich metadata display and an iOS-style frosted glass (毛玻璃) viewing experience.

## What Changes

- **ImagePreview component overhaul**: Replace the current simple modal with a full-screen or near-full-screen preview overlay
- **EXIF metadata panel**: Show camera make/model, lens, aperture, shutter speed, ISO, focal length, date taken, and image dimensions in a clean side panel
- **Frosted glass backdrop**: Apply a blurred backdrop effect (backdrop-filter: blur) behind the preview image, similar to iPhone's 毛玻璃 aesthetic
- **Backend EXIF endpoint**: Add an API endpoint to extract and return EXIF data from uploaded images (or store EXIF at ingest time)
- **Improved navigation**: Thumbnail strip / dot indicators for multi-image browsing within the preview

## Capabilities

### New Capabilities
- `image-exif`: EXIF metadata extraction (backend), storage, and frontend display
- `image-preview-overlay`: Full-screen image preview with frosted glass effect, navigation, and metadata panel

### Modified Capabilities
- *(none — existing frontend capabilities do not have formal specs)*

## Impact

- **Backend**: New `GET /api/images/{id}/exif` endpoint; EXIF extraction at ingest time or on-demand; new DB field (or separate table) for EXIF data
- **Frontend**: `ImagePreview.vue` complete rewrite; new `ExifPanel.vue` component; frosted glass CSS effect (backdrop-filter); potential dependency on `exifr` or similar JS EXIF parser if client-side extraction is preferred
- **Dependencies**: Possibly `exifr` (JS) or `Pillow`/`exifread` (Python) for EXIF extraction
