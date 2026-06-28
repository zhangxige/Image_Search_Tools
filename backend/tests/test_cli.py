import sys
import io
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import tempfile
import shutil

from cli import build_tags, main

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic", ".heif", ".avif"}


class TestBuildTags:
    def test_single_level(self):
        root = Path("/dataset")
        path = Path("/dataset/cats")
        assert build_tags(path, root) == "cats"

    def test_nested(self):
        root = Path("/dataset")
        path = Path("/dataset/animals/cats")
        assert build_tags(path, root) == "animals, cats"

    def test_deep_nested(self):
        root = Path("/dataset")
        path = Path("/dataset/outdoor/nature/sky")
        assert build_tags(path, root) == "outdoor, nature, sky"

    def test_root_level(self):
        root = Path("/dataset")
        assert build_tags(root, root) == ""


class TestDoIngest:
    def test_successful_ingest(self, tmp_path):
        labels = {"cats": ["cat1.jpg", "cat2.jpg"], "dogs": ["dog1.jpg"]}
        for label, files in labels.items():
            d = tmp_path / label
            d.mkdir()
            for fname in files:
                (d / fname).write_text("fake-image-data")

        mock_resp = MagicMock()
        mock_resp.is_success = True

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            out = io.StringIO()
            err = io.StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                args = MagicMock()
                args.directory = str(tmp_path)
                args.url = "http://localhost:8000"
                from cli import do_ingest
                do_ingest(args)

        assert mock_post.call_count == 3
        for call_args in mock_post.call_args_list:
            args, kwargs = call_args
            assert args[0] == "http://localhost:8000/api/ingest"
            assert "files" in kwargs
            assert "tags" in kwargs["data"]

        output = out.getvalue()
        assert "3 succeeded" in output

    def test_ingest_with_failures(self, tmp_path):
        d = tmp_path / "cats"
        d.mkdir()
        (d / "cat1.jpg").write_text("data")
        (d / "cat2.jpg").write_text("data")

        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "cat1.jpg" in str(kwargs.get("files", {})):
                resp.is_success = True
            else:
                resp.is_success = False
                resp.status_code = 500
                resp.text = "Internal Server Error"
            return resp

        with patch("cli.httpx.post", side_effect=side_effect) as mock_post:
            out = io.StringIO()
            err = io.StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                args = MagicMock()
                args.directory = str(tmp_path)
                args.url = "http://localhost:8000"
                from cli import do_ingest
                do_ingest(args)

        assert mock_post.call_count == 2
        output = out.getvalue()
        assert "1 succeeded" in output
        assert "1 failed" in output

    def test_invalid_directory(self):
        args = MagicMock()
        args.directory = "/nonexistent/path"
        args.url = "http://localhost:8000"
        from cli import do_ingest
        with pytest.raises(SystemExit):
            do_ingest(args)

    def test_empty_directory(self, tmp_path):
        (tmp_path / "empty").mkdir()
        args = MagicMock()
        args.directory = str(tmp_path)
        args.url = "http://localhost:8000"
        from cli import do_ingest
        out = io.StringIO()
        err = io.StringIO()
        with patch("sys.stdout", out), patch("sys.stderr", err):
            do_ingest(args)
        assert "0 succeeded" in out.getvalue()

    def test_tag_from_directory_name(self, tmp_path):
        d = tmp_path / "wildlife"
        d.mkdir()
        (d / "img.jpg").write_text("data")

        mock_resp = MagicMock()
        mock_resp.is_success = True

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            out = io.StringIO()
            with patch("sys.stdout", out):
                args = MagicMock()
                args.directory = str(tmp_path)
                args.url = "http://localhost:8000"
                from cli import do_ingest
                do_ingest(args)

        _, kwargs = mock_post.call_args
        assert kwargs["data"]["tags"] == "wildlife"


class TestDoSearch:
    def test_successful_search(self, tmp_path):
        for fname in ["query1.jpg", "query2.png"]:
            (tmp_path / fname).write_text("fake-data")

        mock_result = {
            "results": [
                {
                    "image": {
                        "id": 1,
                        "filename": "abc.jpg",
                        "original_filename": "match.jpg",
                        "tags": "nature, sky",
                        "file_size": 100,
                        "width": 100,
                        "height": 100,
                        "mime_type": "image/jpeg",
                        "is_hdr": False,
                        "hdr_format": None,
                        "created_at": "2026-01-01T00:00:00",
                    },
                    "distance": 0.85,
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = mock_result

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            out = io.StringIO()
            with patch("sys.stdout", out):
                args = MagicMock()
                args.directory = str(tmp_path)
                args.url = "http://localhost:8000"
                args.top_k = 5
                from cli import do_search
                do_search(args)

        assert mock_post.call_count == 2
        for call_args in mock_post.call_args_list:
            assert call_args[0][0] == "http://localhost:8000/api/search"

        output = out.getvalue()
        assert "match.jpg" in output
        assert "nature, sky" in output
        assert "85.0%" in output

    def test_search_custom_top_k(self, tmp_path):
        (tmp_path / "q.jpg").write_text("data")

        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"results": []}

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            args = MagicMock()
            args.directory = str(tmp_path)
            args.url = "http://localhost:8000"
            args.top_k = 10
            from cli import do_search
            do_search(args)

        _, kwargs = mock_post.call_args
        assert kwargs["data"]["top_k"] == "10"

    def test_search_server_error(self, tmp_path):
        (tmp_path / "q.jpg").write_text("data")

        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.status_code = 500
        mock_resp.text = "Error"

        with patch("cli.httpx.post", return_value=mock_resp):
            out = io.StringIO()
            err = io.StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                args = MagicMock()
                args.directory = str(tmp_path)
                args.url = "http://localhost:8000"
                args.top_k = 5
                from cli import do_search
                do_search(args)

        assert "Error" in err.getvalue()

    def test_search_no_images(self, tmp_path):
        args = MagicMock()
        args.directory = str(tmp_path)
        args.url = "http://localhost:8000"
        args.top_k = 5
        from cli import do_search
        out = io.StringIO()
        with patch("sys.stdout", out):
            do_search(args)
        assert "No images found" in out.getvalue()


class TestArgparse:
    def test_help(self):
        with patch("sys.argv", ["cli.py", "--help"]):
            with pytest.raises(SystemExit):
                main()

    def test_ingest_help(self):
        with patch("sys.argv", ["cli.py", "ingest", "--help"]):
            with pytest.raises(SystemExit):
                main()

    def test_search_help(self):
        with patch("sys.argv", ["cli.py", "search", "--help"]):
            with pytest.raises(SystemExit):
                main()

    def test_no_command(self):
        with patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit):
                main()

    def test_ingest_default_url(self, tmp_path):
        d = tmp_path / "test"
        d.mkdir()
        (d / "img.jpg").write_text("data")
        mock_resp = MagicMock()
        mock_resp.is_success = True

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            with patch("sys.argv", ["cli.py", "ingest", str(tmp_path)]):
                main()

        assert mock_post.called
        url = mock_post.call_args[0][0]
        assert url.startswith("http://localhost:8000")

    def test_search_custom_url(self, tmp_path):
        (tmp_path / "q.jpg").write_text("data")
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"results": []}

        with patch("cli.httpx.post", return_value=mock_resp) as mock_post:
            with patch("sys.argv", ["cli.py", "--url", "http://other:9000", "search", str(tmp_path)]):
                main()

        url = mock_post.call_args[0][0]
        assert url.startswith("http://other:9000")
