import datetime

from app.schemas import ImageResponse, ImageUpdate, SearchResult, IngestionLogResponse, IngestionResult


class TestImageResponse:
    def test_from_attributes(self):
        now = datetime.datetime.utcnow()
        data = {
            "id": 1,
            "filename": "abc.jpg",
            "original_filename": "test.jpg",
            "file_size": 1024,
            "width": 299,
            "height": 299,
            "mime_type": "image/jpeg",
            "tags": "nature,sky",
            "created_at": now,
        }
        resp = ImageResponse.model_validate(data)
        assert resp.id == 1
        assert resp.filename == "abc.jpg"
        assert resp.tags == "nature,sky"
        assert resp.created_at == now

    def test_optional_fields_default_none(self):
        now = datetime.datetime.utcnow()
        data = {
            "id": 2,
            "filename": "no-meta.jpg",
            "original_filename": "no-meta.jpg",
            "created_at": now,
        }
        resp = ImageResponse.model_validate(data)
        assert resp.file_size is None
        assert resp.width is None
        assert resp.tags == ""

    def test_serialization(self):
        now = datetime.datetime.utcnow()
        data = {
            "id": 3,
            "filename": "ser.jpg",
            "original_filename": "ser.jpg",
            "file_size": 512,
            "width": 100,
            "height": 200,
            "mime_type": "image/png",
            "tags": "test",
            "created_at": now,
        }
        resp = ImageResponse.model_validate(data)
        d = resp.model_dump()
        assert d["id"] == 3
        assert d["tags"] == "test"


class TestImageUpdate:
    def test_partial_update_tags(self):
        update = ImageUpdate(tags="new-tag")
        assert update.tags == "new-tag"

    def test_empty_update(self):
        update = ImageUpdate()
        assert update.tags is None


class TestSearchResult:
    def test_construct(self):
        now = datetime.datetime.utcnow()
        img = ImageResponse.model_validate({
            "id": 1,
            "filename": "a.jpg",
            "original_filename": "a.jpg",
            "created_at": now,
        })
        result = SearchResult(image=img, distance=0.85)
        assert result.image.id == 1
        assert 0 <= result.distance <= 1


class TestIngestionLogResponse:
    def test_from_attributes(self):
        now = datetime.datetime.utcnow()
        data = {
            "id": 10,
            "operation": "ingest",
            "status": "success",
            "image_id": 1,
            "filename": "test.jpg",
            "message": "OK",
            "created_at": now,
        }
        log = IngestionLogResponse.model_validate(data)
        assert log.operation == "ingest"
        assert log.status == "success"

    def test_nullable_fields(self):
        now = datetime.datetime.utcnow()
        data = {
            "id": 11,
            "operation": "ingest",
            "status": "failed",
            "created_at": now,
        }
        log = IngestionLogResponse.model_validate(data)
        assert log.image_id is None
        assert log.filename is None
        assert log.message is None


class TestIngestionResult:
    def test_response_shape(self):
        result = IngestionResult(success=[], failed=[], total=0)
        assert result.success == []
        assert result.failed == []
        assert result.total == 0
