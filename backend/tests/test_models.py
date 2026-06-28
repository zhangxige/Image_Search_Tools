import datetime
import pytest
import numpy as np

from app.models import ImageRecord, FeatureVector, IngestionLog


class TestImageRecord:
    def test_create_record(self, db_session):
        record = ImageRecord(
            filename="abc.jpg",
            original_filename="test.jpg",
            file_size=1024,
            width=299,
            height=299,
            mime_type="image/jpeg",
            tags="nature,sky",
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.filename == "abc.jpg"
        assert record.original_filename == "test.jpg"
        assert record.file_size == 1024
        assert record.width == 299
        assert record.height == 299
        assert record.mime_type == "image/jpeg"
        assert record.tags == "nature,sky"
        assert isinstance(record.created_at, datetime.datetime)

    def test_cascade_delete_feature(self, db_session):
        record = ImageRecord(filename="cascade.jpg", original_filename="cascade.jpg")
        db_session.add(record)
        db_session.flush()

        vec = np.random.randn(2048).astype(np.float32)
        feature = FeatureVector(image_id=record.id, vector=vec.tobytes())
        db_session.add(feature)
        db_session.commit()

        assert db_session.query(FeatureVector).count() == 1

        db_session.delete(record)
        db_session.commit()

        assert db_session.query(FeatureVector).count() == 0

    def test_cascade_delete_logs(self, db_session):
        record = ImageRecord(filename="logcascade.jpg", original_filename="logcascade.jpg")
        db_session.add(record)
        db_session.flush()

        log = IngestionLog(
            operation="ingest", status="success", image_id=record.id, filename="logcascade.jpg"
        )
        db_session.add(log)
        db_session.commit()

        assert db_session.query(IngestionLog).count() == 1
        db_session.delete(record)
        db_session.commit()
        assert db_session.query(IngestionLog).count() == 0


class TestFeatureVector:
    def test_store_and_retrieve_vector(self, db_session):
        record = ImageRecord(filename="vec_test.jpg", original_filename="vec_test.jpg")
        db_session.add(record)
        db_session.flush()

        original_vec = np.random.randn(2048).astype(np.float32)
        feat = FeatureVector(image_id=record.id, vector=original_vec.tobytes(), dimension=2048)
        db_session.add(feat)
        db_session.commit()

        retrieved = db_session.query(FeatureVector).first()
        loaded = np.frombuffer(retrieved.vector, dtype=np.float32)
        assert np.allclose(loaded, original_vec)
        assert retrieved.dimension == 2048

    def test_unique_image_id(self, db_session):
        record = ImageRecord(filename="unique_test.jpg", original_filename="unique_test.jpg")
        db_session.add(record)
        db_session.flush()

        vec = np.random.randn(2048).astype(np.float32).tobytes()
        db_session.add(FeatureVector(image_id=record.id, vector=vec))
        db_session.commit()

        with pytest.raises(Exception):
            db_session.add(FeatureVector(image_id=record.id, vector=vec))
            db_session.commit()

    def test_relationship(self, db_session):
        record = ImageRecord(filename="rel.jpg", original_filename="rel.jpg")
        db_session.add(record)
        db_session.flush()

        vec = np.random.randn(2048).astype(np.float32).tobytes()
        feat = FeatureVector(image_id=record.id, vector=vec)
        db_session.add(feat)
        db_session.commit()

        assert feat.image.id == record.id
        assert record.feature.id == feat.id


class TestIngestionLog:
    def test_create_log(self, db_session):
        record = ImageRecord(filename="log_test.jpg", original_filename="log_test.jpg")
        db_session.add(record)
        db_session.flush()

        log = IngestionLog(
            operation="ingest",
            status="success",
            image_id=record.id,
            filename="log_test.jpg",
            message="OK",
        )
        db_session.add(log)
        db_session.commit()

        assert log.id is not None
        assert log.operation == "ingest"
        assert log.status == "success"
        assert log.image_id == record.id
        assert log.message == "OK"

    def test_relationship(self, db_session):
        record = ImageRecord(filename="log_rel.jpg", original_filename="log_rel.jpg")
        db_session.add(record)
        db_session.flush()

        log = IngestionLog(operation="ingest", status="success", image_id=record.id)
        db_session.add(log)
        db_session.commit()

        assert log.image.id == record.id
        assert record.logs[0].id == log.id

    def test_nullable_image_id(self, db_session):
        log = IngestionLog(operation="ingest", status="failed", message="error")
        db_session.add(log)
        db_session.commit()
        assert log.image_id is None
