## ADDED Requirements

### Requirement: Test dependencies are declared
The project SHALL declare `pytest`, `httpx`, and `pytest-cov` as optional dev dependencies.

#### Scenario: pytest is installable
- **WHEN** `uv sync --dev` is run
- **THEN** `pytest` SHALL be available as a CLI command

#### Scenario: httpx is importable
- **WHEN** `import httpx` is executed in a Python test context
- **THEN** it SHALL not raise `ImportError`

### Requirement: conftest.py provides shared fixtures
The `backend/tests/conftest.py` SHALL provide reusable fixtures for all test modules.

#### Scenario: db_session fixture creates in-memory SQLite
- **WHEN** a test requests the `db_session` fixture
- **THEN** it SHALL receive a SQLAlchemy session backed by an in-memory SQLite database with all tables created

#### Scenario: client fixture provides FastAPI TestClient
- **WHEN** a test requests the `client` fixture
- **THEN** it SHALL receive a Starlette `TestClient` wired to the FastAPI app with the test `db_session` overridden

#### Scenario: mock_feature_extractor fixture mocks extract_feature
- **WHEN** a test requests the `mock_feature_extractor` fixture
- **THEN** calls to `feature_extractor.extract_feature` SHALL return a predictable 2048-d L2-normalized vector without loading PyTorch

#### Scenario: sample_image fixture provides a valid test image
- **WHEN** a test requests the `sample_image` fixture
- **THEN** it SHALL receive a BytesIO object containing a small valid PNG image

### Requirement: Coverage reporting works
The test suite SHALL support coverage measurement via `pytest-cov`.

#### Scenario: Coverage report is generated
- **WHEN** `pytest --cov=app` is run from the `backend/` directory
- **THEN** a coverage summary SHALL be printed to stdout with module-level percentages
