import io
import pytest
from PIL import Image, UnidentifiedImageError


def _ingest_image(client, name="seed.png"):
    buf = io.BytesIO()
    Image.new("RGB", (299, 299), color="red").save(buf, format="PNG")
    buf.seek(0)
    resp = client.post("/api/ingest", files={"files": (name, buf, "image/png")})
    return resp.json()


import pytest


class TestSearch:
    def test_search_returns_results(self, client, sample_image):
        _ingest_image(client)
        sample_image.seek(0)
        resp = client.post(
            "/api/search",
            files={"files": ("query.png", sample_image, "image/png")},
            data={"top_k": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) >= 1
        result = data["results"][0]
        assert "image" in result
        assert "distance" in result
        assert isinstance(result["distance"], float)

    def test_search_top_k(self, client, sample_image):
        for i in range(5):
            _ingest_image(client, f"seed_{i}.png")

        sample_image.seek(0)
        resp = client.post(
            "/api/search",
            files={"files": ("query.png", sample_image, "image/png")},
            data={"top_k": 3},
        )
        assert resp.status_code == 200
        assert len(resp.json()["results"]) <= 3

    def test_search_empty_db_returns_empty(self, client, sample_image):
        sample_image.seek(0)
        resp = client.post(
            "/api/search",
            files={"files": ("query.png", sample_image, "image/png")},
            data={"top_k": 5},
        )
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    def test_search_no_files_returns_400(self, client):
        resp = client.post("/api/search", data={"top_k": 5})
        assert resp.status_code in (400, 422)

    def test_search_invalid_file_returns_error(self, client):
        with pytest.raises(UnidentifiedImageError):
            client.post(
                "/api/search",
                files={"files": ("bad.txt", io.BytesIO(b"not an image"), "text/plain")},
            )
