import io
from PIL import Image


class TestIngest:
    def test_single_ingestion(self, client, sample_image):
        sample_image.seek(0)
        resp = client.post(
            "/api/ingest",
            files={"files": ("test.png", sample_image, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["success"]) == 1
        assert data["success"][0]["original_filename"] == "test.png"
        assert "id" in data["success"][0]
        assert "filename" in data["success"][0]

    def test_ingest_with_tags(self, client, sample_image):
        sample_image.seek(0)
        resp = client.post(
            "/api/ingest",
            files={"files": ("tagged.png", sample_image, "image/png")},
            data={"tags": "nature,sky"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"][0]["tags"] == "nature,sky"

    def test_batch_ingestion(self, client, sample_image):
        def _img(name):
            buf = io.BytesIO()
            Image.new("RGB", (50, 50), color="red").save(buf, format="PNG")
            buf.seek(0)
            return (name, buf, "image/png")

        resp = client.post(
            "/api/ingest",
            files=[
                ("files", _img("a.png")),
                ("files", _img("b.png")),
                ("files", _img("c.png")),
            ],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["success"]) == 3

    def test_ingest_invalid_file(self, client):
        resp = client.post(
            "/api/ingest",
            files={"files": ("bad.txt", io.BytesIO(b"not an image"), "text/plain")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["failed"]) == 1
        assert data["failed"][0]["filename"] == "bad.txt"
