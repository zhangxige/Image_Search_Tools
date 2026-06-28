import io
from PIL import Image


def _ingest(client, name="img.png", tags=""):
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), color="red").save(buf, format="PNG")
    buf.seek(0)
    data = {"tags": tags} if tags else {}
    resp = client.post("/api/ingest", files={"files": (name, buf, "image/png")}, data=data)
    return resp.json()["success"][0]


class TestListImages:
    def test_list_all(self, client):
        for i in range(3):
            _ingest(client, f"img_{i}.png")
        resp = client.get("/api/images?skip=0&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_list_pagination(self, client):
        for i in range(5):
            _ingest(client, f"page_{i}.png")
        resp = client.get("/api/images?skip=2&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_filter_by_tag(self, client):
        _ingest(client, "a.png", tags="nature")
        _ingest(client, "b.png", tags="city")
        _ingest(client, "c.png", tags="nature,sky")

        resp = client.get("/api/images?tag=nature")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_filter_no_match(self, client):
        _ingest(client, "a.png", tags="nature")
        resp = client.get("/api/images?tag=ocean")
        assert resp.status_code == 200
        assert resp.json() == []


class TestCountImages:
    def test_count_all(self, client):
        for i in range(4):
            _ingest(client, f"c_{i}.png")
        resp = client.get("/api/images/count")
        assert resp.status_code == 200
        assert resp.json()["count"] == 4

    def test_count_filtered(self, client):
        _ingest(client, "a.png", tags="dog")
        _ingest(client, "b.png", tags="cat")
        _ingest(client, "c.png", tags="dog,pet")
        resp = client.get("/api/images/count?tag=dog")
        assert resp.status_code == 200
        assert resp.json()["count"] == 2


class TestDeleteImage:
    def test_delete_existing(self, client):
        img = _ingest(client)
        resp = client.delete(f"/api/images/{img['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == img["id"]

        # Verify it's gone
        resp = client.get("/api/images")
        assert resp.json() == []

    def test_delete_non_existent(self, client):
        resp = client.delete("/api/images/9999")
        assert resp.status_code == 404

    def test_batch_delete(self, client):
        ids = [_ingest(client, f"batch_{i}.png")["id"] for i in range(3)]
        resp = client.delete(f"/api/images?image_ids={ids[0]}&image_ids={ids[1]}")
        assert resp.status_code == 200
        data = resp.json()
        assert sorted(data["deleted"]) == sorted([ids[0], ids[1]])
        assert data["not_found"] == []

        resp = client.get("/api/images")
        assert len(resp.json()) == 1

    def test_batch_delete_mixed(self, client):
        ids = [_ingest(client, "exists.png")["id"]]
        resp = client.delete(f"/api/images?image_ids={ids[0]}&image_ids=9999")
        assert resp.status_code == 200
        assert resp.json()["deleted"] == [ids[0]]
        assert resp.json()["not_found"] == [9999]


class TestUpdateImage:
    def test_update_tags(self, client):
        img = _ingest(client, "update.png", tags="old")
        resp = client.patch(
            f"/api/images/{img['id']}",
            json={"tags": "new-tag"},
        )
        assert resp.status_code == 200
        assert resp.json()["tags"] == "new-tag"

    def test_update_non_existent(self, client):
        resp = client.patch("/api/images/9999", json={"tags": "test"})
        assert resp.status_code == 404


class TestLogs:
    def test_list_logs(self, client):
        _ingest(client)
        resp = client.get("/api/images/logs?skip=0&limit=10")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_log_after_ingest(self, client):
        _ingest(client, "log_check.png")
        resp = client.get("/api/images/logs")
        logs = resp.json()
        # Most recent log first
        assert logs[0]["operation"] == "ingest"
        assert logs[0]["status"] == "success"
        assert logs[0]["filename"] == "log_check.png"
