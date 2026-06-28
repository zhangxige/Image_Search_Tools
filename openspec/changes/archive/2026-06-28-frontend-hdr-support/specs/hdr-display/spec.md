## ADDED Requirements

### Requirement: Gallery card shows HDR badge
The gallery image card SHALL display an HDR badge (icon + tooltip) when the image is HDR.

#### Scenario: HDR badge on card
- **WHEN** a gallery card displays an image with `is_hdr = True`
- **THEN** the card SHALL show an HDR icon in the top-right corner of the image wrapper

#### Scenario: Tooltip on hover
- **WHEN** the user hovers over the HDR badge
- **THEN** a tooltip SHALL appear showing the `hdr_format` text (e.g., "Apple HEIC 10-bit")

#### Scenario: Non-HDR card
- **WHEN** an image has `is_hdr = False`
- **THEN** no HDR badge SHALL be shown

### Requirement: ImagePreview shows HDR badge
The ImagePreview overlay SHALL display an HDR badge in the top bar for HDR images.

#### Scenario: HDR badge in preview
- **WHEN** the preview opens for an HDR image
- **THEN** the top-left info area SHALL display an HDR icon with the format label

#### Scenario: Consistent with gallery badge
- **WHEN** the same image is viewed in both gallery and preview
- **THEN** the HDR badge SHALL be present in both locations

### Requirement: Browser HDR display
The frontend SHALL use CSS media queries to enable HDR display in supporting browsers.

#### Scenario: HDR display enabled
- **WHEN** the browser supports `dynamic-range: high` and the image is HDR
- **THEN** the preview image SHALL use `color-gamut: p3` CSS for wider color fidelity

#### Scenario: SDR fallback
- **WHEN** the browser does not support `dynamic-range: high`
- **THEN** the image SHALL display in standard SDR with no HDR-specific CSS

### Requirement: HDR badge component
The system SHALL provide a reusable `<HdrBadge>` Vue component.

#### Scenario: Component props
- **WHEN** the `<HdrBadge>` component is used
- **THEN** it SHALL accept `format` (string) and `size` (small/large) props

#### Scenario: Component renders
- **WHEN** `format` is provided
- **THEN** the component SHALL render an HDR icon with a tooltip showing the format text
