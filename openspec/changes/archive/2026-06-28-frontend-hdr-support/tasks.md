## 1. Database Migration

- [x] 1.1 Add `is_hdr` Boolean (default false, indexed) and `hdr_format` String(50) nullable columns to `ImageRecord`
- [x] 1.2 Add migration in `_migrate()` for both new columns with IF NOT EXISTS

## 2. Backend HDR Detection

- [x] 2.1 Add `detect_hdr(exif_data: dict, mime_type: str) -> tuple[bool, str | None]` to `exif_utils.py`
- [x] 2.2 Implement ColorSpace tag (40961) heuristic: Adobe RGB / Uncalibrated + ICC profile
- [x] 2.3 Implement Gamma tag (42240) heuristic for HDR transfer function detection
- [x] 2.4 Implement MakerNote (37500) heuristic for phone-specific HDR indicators (Apple, Samsung, Vivo, Huawei)
- [x] 2.5 Integrate HDR detection into ingest router, store `is_hdr` and `hdr_format` on `ImageRecord`

## 3. Backend Schema Updates

- [x] 3.1 Add `is_hdr: bool = False` and `hdr_format: Optional[str] = None` to `ImageResponse` in schemas.py
- [x] 3.2 Ensure existing images default to `is_hdr = False`

## 4. Frontend HdrBadge Component

- [x] 4.1 Create `HdrBadge.vue` with HDR icon SVG + tooltip on hover
- [x] 4.2 Support `format` (string) and `size` (small/large) props
- [x] 4.3 Style tooltip with dark background and format text

## 5. Frontend Gallery Card Integration

- [x] 5.1 Add HDR badge to gallery card `image-wrapper` in `pages/index.vue`
- [x] 5.2 Show badge only when `img.is_hdr` is true
- [x] 5.3 Pass `img.hdr_format` to tooltip

## 6. Frontend ImagePreview Integration

- [x] 6.1 Add HDR badge to `ImagePreview.vue` top-bar, next to filename
- [x] 6.2 Use large variant of HdrBadge for preview context

## 7. CSS HDR Display

- [x] 7.1 Add `@media (dynamic-range: high)` CSS rules in `assets/main.css` or ImagePreview styles
- [x] 7.2 Add `@media (color-gamut: p3)` for wide color gamut enhancement
- [x] 7.3 Ensure SDR fallback for non-supporting browsers

## 8. Verification

- [x] 8.1 Run backend syntax check / type check
- [ ] 8.2 Manually verify HDR badge appears on gallery cards and preview
- [ ] 8.3 Verify tooltip displays correct format text
- [ ] 8.4 Verify non-HDR images show no badge
- [ ] 8.5 Test with test images containing known HDR EXIF data
