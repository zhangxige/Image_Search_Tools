## ADDED Requirements

### Requirement: useTheme composable tests
The useTheme composable SHALL be tested for correct theme toggling, localStorage persistence, and initial state detection.

#### Scenario: Toggle switches theme
- **WHEN** `toggle()` is called on a light-themed composable
- **THEN** the theme SHALL switch to dark and `isDark` SHALL be `true`

#### Scenario: Toggle switches back to light
- **WHEN** `toggle()` is called on a dark-themed composable
- **THEN** the theme SHALL switch to light and `isDark` SHALL be `false`

#### Scenario: Preference persists in localStorage
- **WHEN** `toggle()` is called and composable is re-created
- **THEN** the restored theme SHALL match the previously toggled value

#### Scenario: Falls back to prefers-color-scheme
- **WHEN** localStorage has no stored preference and system prefers dark
- **THEN** initial `isDark` SHALL be `true`

#### Scenario: Sets data-theme attribute on html
- **WHEN** theme is toggled to dark
- **THEN** `document.documentElement.dataset.theme` SHALL be `"dark"`

### Requirement: NavBar component tests
The NavBar SHALL render navigation links, GitHub link, and theme toggle button correctly.

#### Scenario: Renders all nav links
- **WHEN** NavBar is rendered
- **THEN** it SHALL display links for Gallery, Upload, Search, and Logs

#### Scenario: GitHub link uses runtime config
- **WHEN** runtime config has `githubRepo` set to `"owner/repo"`
- **THEN** the GitHub link SHALL point to `https://github.com/owner/repo`

#### Scenario: Theme toggle calls composable
- **WHEN** theme toggle button is clicked
- **THEN** `isDark` SHALL toggle and the icon SHALL reflect the current theme

### Requirement: ImageCard component tests
ImageCard SHALL display image metadata and emit click events.

#### Scenario: Displays filename and metadata
- **WHEN** ImageCard is given `filename`, `width`, `height`, `fileSize` props
- **THEN** it SHALL render the filename, dimensions, and formatted file size

#### Scenario: Emits click event
- **WHEN** ImageCard is clicked
- **THEN** it SHALL emit a `click` event

### Requirement: AppFooter component tests
AppFooter SHALL render copyright text and project attribution.

#### Scenario: Renders current year
- **WHEN** AppFooter is rendered
- **THEN** it SHALL display the current copyright year

#### Scenario: Renders project attribution
- **WHEN** AppFooter is rendered
- **THEN** it SHALL display "Powered by Xception + FAISS"

### Requirement: Default layout tests
The default layout SHALL render NavBar, slot content, and AppFooter.

#### Scenario: Renders NavBar
- **WHEN** default layout renders with slot content
- **THEN** NavBar SHALL be present at the top

#### Scenario: Renders AppFooter
- **WHEN** default layout renders with slot content
- **THEN** AppFooter SHALL be present at the bottom
