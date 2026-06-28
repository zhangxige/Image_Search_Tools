## ADDED Requirements

### Requirement: Full-screen overlay with frosted glass backdrop
The image preview SHALL display as a full-viewport overlay with a frosted glass (毛玻璃) aesthetic using CSS `backdrop-filter: blur()`.

#### Scenario: Overlay opens
- **WHEN** a user double-clicks an image in the gallery
- **THEN** a full-screen overlay SHALL appear with the image centered and a blurred background

#### Scenario: Frosted glass effect
- **WHEN** the overlay is open
- **THEN** the overlay background SHALL use a duplicate image as CSS `background-image`, scaled up (120%+) and blurred with `backdrop-filter: blur(20px)`, with a semi-transparent dark overlay

#### Scenario: Fallback without blur support
- **WHEN** the browser does not support `backdrop-filter`
- **THEN** a solid `rgba(0,0,0,0.85)` background SHALL be used as fallback

### Requirement: Image display
The preview overlay SHALL display the full-resolution image centered with `object-fit: contain`.

#### Scenario: Image scales to viewport
- **WHEN** the overlay opens
- **THEN** the image SHALL be displayed at maximum size fitting within the viewport while preserving aspect ratio

#### Scenario: Image load error
- **WHEN** the image fails to load
- **THEN** a placeholder with "Load Failed" text SHALL be displayed

### Requirement: EXIF metadata panel
The overlay SHALL include a slide-in side panel displaying EXIF metadata for the current image.

#### Scenario: EXIF panel toggle
- **WHEN** the user clicks an info (i) button in the overlay
- **THEN** a right-side panel SHALL slide in showing grouped EXIF metadata (Camera, Settings, File sections)

#### Scenario: No EXIF data
- **WHEN** the image has no EXIF data
- **THEN** the panel SHALL display "No EXIF data available"

#### Scenario: Panel closes
- **WHEN** the user clicks the close button on the panel or clicks outside it
- **THEN** the panel SHALL slide out

### Requirement: Keyboard navigation
The overlay SHALL support keyboard navigation for browsing images.

#### Scenario: Arrow keys navigate
- **WHEN** the overlay is open and the user presses ArrowLeft
- **THEN** the previous image in the gallery SHALL be displayed

#### Scenario: ArrowRight navigates forward
- **WHEN** the overlay is open and the user presses ArrowRight
- **THEN** the next image SHALL be displayed

#### Scenario: Escape closes overlay
- **WHEN** the user presses Escape
- **THEN** the overlay SHALL close

### Requirement: Tag editing preserved
The overlay SHALL preserve the existing inline tag editing functionality.

#### Scenario: Tags displayed
- **WHEN** the overlay is open for an image with tags
- **THEN** the tags SHALL be displayed as pill badges below the image

#### Scenario: Tags editable
- **WHEN** the user clicks the edit (✎) button
- **THEN** a text input SHALL appear for comma-separated tag editing, with Save and Cancel buttons

### Requirement: Prev/Next navigation buttons
The overlay SHALL have previous and next navigation arrow buttons.

#### Scenario: Navigate to previous
- **WHEN** the user clicks the left arrow button
- **THEN** the previous image SHALL be displayed

#### Scenario: Navigate to next
- **WHEN** the user clicks the right arrow button
- **THEN** the next image SHALL be displayed

#### Scenario: Disabled at boundaries
- **WHEN** viewing the first image, the prev button SHALL be disabled
- **WHEN** viewing the last image, the next button SHALL be disabled
