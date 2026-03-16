from typing import Any
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import torch

from app.services.transcription import Speech2Text


class TestSpeech2Text:

    @pytest.fixture(scope="session")
    def mock_model(self):
        with patch('app.services.transcription.Speech2TextForConditionalGeneration') as mock:
            mock_instance = MagicMock()
            mock.from_pretrained.return_value = mock_instance
            yield mock_instance

    @pytest.fixture(scope="session")
    def mock_processor(self):
        with patch('app.services.transcription.Speech2TextProcessor') as mock:
            mock_instance = MagicMock()
            mock.from_pretrained.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def speech2text(self, mock_model: MagicMock, mock_processor: MagicMock):
        return Speech2Text()

    @pytest.fixture
    def mock_audio_data(self):
        audio_array = np.random.rand(16000).astype(np.float32)
        sample_rate = 16000
        return audio_array, sample_rate

    @pytest.mark.unit
    def test_init_loads_model(self, mock_model: MagicMock, mock_processor: MagicMock):
        s2t = Speech2Text()
        assert s2t.model is not None
        assert s2t.processor is not None

    @pytest.mark.unit
    @patch('app.services.transcription.librosa.load')
    def test_prepare_audio_success(self, mock_librosa, speech2text: Any, mock_audio_data: tuple):
        mock_librosa.return_value = mock_audio_data
        audio_bytes = b"fake audio bytes"

        audio_array, sr = speech2text.prepare_audio(audio_bytes)

        assert isinstance(audio_array, np.ndarray)
        assert sr == 16000

    @pytest.mark.unit
    @patch('app.services.transcription.librosa.load')
    def test_transcribe_audio(self, mock_librosa, speech2text: Any, mock_audio_data: tuple):
        mock_librosa.return_value = mock_audio_data

        speech2text.processor.return_value = {
            "input_features": torch.randn(1, 80, 100),
            "attention_mask": torch.ones(1, 100)
        }
        speech2text.model.generate.return_value = torch.tensor([[1, 2, 3]])
        speech2text.processor.batch_decode.return_value = ["hello world"]

        result = speech2text.transcribe_audio(b"fake audio bytes")

        assert isinstance(result, str)
        assert result == "hello world"
        speech2text.model.generate.assert_called_once()
        speech2text.processor.batch_decode.assert_called_once()
