from unittest.mock import patch, MagicMock
import numpy as np
import torch
from PIL import Image
import io

from app.feature_extractor import extract_feature, extract_feature_from_path


class TestExtractFeature:
    def test_extract_feature_returns_correct_shape_and_norm(self):
        # Mock the model to return a known 2048-d tensor
        mock_model = MagicMock()
        mock_output = torch.randn(1, 2048)
        mock_model.return_value = mock_output
        mock_model.eval.return_value = mock_model

        with patch("app.feature_extractor.get_model", return_value=mock_model):
            with patch("app.feature_extractor.get_device", return_value=torch.device("cpu")):
                img = Image.new("RGB", (299, 299), color="blue")
                feat = extract_feature(img)

                assert feat.shape == (2048,)
                assert feat.dtype == np.float32
                norm = np.linalg.norm(feat)
                assert abs(norm - 1.0) < 1e-5

    def test_extract_feature_normalizes_non_unit(self):
        mock_model = MagicMock()
        # Return a non-normalized vector
        output = torch.tensor([[3.0, 4.0] + [0.0] * 2046], dtype=torch.float32)
        mock_model.return_value = output
        mock_model.eval.return_value = mock_model

        with patch("app.feature_extractor.get_model", return_value=mock_model):
            with patch("app.feature_extractor.get_device", return_value=torch.device("cpu")):
                img = Image.new("RGB", (299, 299), color="green")
                feat = extract_feature(img)

                # 3-4-5 triangle norm is 5
                assert abs(feat[0] - 0.6) < 1e-5
                assert abs(feat[1] - 0.8) < 1e-5
                assert abs(np.linalg.norm(feat) - 1.0) < 1e-5

    def test_extract_feature_handles_rgba_image(self):
        mock_model = MagicMock()
        mock_model.return_value = torch.randn(1, 2048)
        mock_model.eval.return_value = mock_model

        with patch("app.feature_extractor.get_model", return_value=mock_model):
            with patch("app.feature_extractor.get_device", return_value=torch.device("cpu")):
                img = Image.new("RGBA", (299, 299), color=(255, 0, 0, 128))
                feat = extract_feature(img)
                assert feat.shape == (2048,)


class TestExtractFeatureFromPath:
    def test_extract_from_path(self, tmp_path):
        mock_model = MagicMock()
        mock_model.return_value = torch.randn(1, 2048)
        mock_model.eval.return_value = mock_model

        img_path = tmp_path / "test.png"
        Image.new("RGB", (299, 299), color="red").save(img_path)

        with patch("app.feature_extractor.get_model", return_value=mock_model):
            with patch("app.feature_extractor.get_device", return_value=torch.device("cpu")):
                feat = extract_feature_from_path(str(img_path))
                assert feat.shape == (2048,)
                assert abs(np.linalg.norm(feat) - 1.0) < 1e-5
