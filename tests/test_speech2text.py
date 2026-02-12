import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import torch

from src.audio_processing.speech2text import Speech2Text


class TestSpeech2Text:
    
    @pytest.fixture(scope = "session")
    def mock_model(self):
        """Mock the Hugging Face model to avoid loading in tests."""
        with patch('src.audio_processing.speech2text.Speech2TextForConditionalGeneration') as mock:
            mock_instance = MagicMock()
            mock.from_pretrained.return_value = mock_instance
            yield mock_instance
            
    @pytest.fixture(scope = "session")
    def mock_processor(self):
        with patch('src.audio_processing.speech2text.Speech2TextProcessor') as mock:
            mock_instance = MagicMock()
            mock.from_pretrained.return_value = mock_instance
            yield mock_instance
            
    @pytest.fixture
    def speech2text(self, mock_model, mock_processor):
        return Speech2Text()
    
    @pytest.fixture
    def sample_audio_file(self, tmp_path):
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        return audio_file
    
    @pytest.fixture    
    def mock_audio_data(self):
        audio_array = np.random.rand(16000)
        sample_rate = 16000
        return audio_array, sample_rate


    @pytest.mark.unit
    def test_init_loads_model(self, mock_model, mock_processor):
        s2t = Speech2Text()
        
        assert s2t.model is not None
        assert s2t.processor is not None
        
    @pytest.mark.unit
    def test_prepare_audio_file(self, speech2text, filename = "nonexistent.mp3"):
        with pytest.raises(FileNotFoundError, match = f"Audio File not Found: {filename}"):
            speech2text.prepare_audio(filename)
        
    @pytest.mark.unit
    @patch('src.audio_processing.speech2text.librosa.load') #patch sieht was es returnen soll
    def test_prepare_audio_success(self, mock_librosa, speech2text, sample_audio_file, mock_audio_data):
        
        mock_librosa.return_value = mock_audio_data
        audio_array, sr = speech2text.prepare_audio(sample_audio_file) #mock wird gecalled und returned audio_array, sr
        
        assert isinstance(audio_array, np.ndarray)
        assert sr == 16000
        mock_librosa.assert_called_once_with(sample_audio_file, sr=16000) #wenn einmal gecalled
        
    
    @pytest.mark.unit
    @patch('src.audio_processing.speech2text.torch.no_grad')
    @patch('src.audio_processing.speech2text.librosa.load') #patch sieht was es returnen soll
    def test_transcribe_audio(self, mock_librosa, mock_no_grad, speech2text, sample_audio_file, mock_audio_data):
        
        mock_librosa.return_value = mock_audio_data
        
        
        speech2text.processor.return_value =  {
            "input_features": torch.randn(1, 80, 100),
            "attention_mask": torch.ones(1, 100)
        }
        
        speech2text.model.return_value = torch.tensor([[1,2,3]])
        
        speech2text.processor.batch_decode.return_value = ["hello world"]
        
        result = speech2text.transcribe_audio(sample_audio_file)
        
        assert isinstance(result, str)
        assert result == "hello world"
        
        mock_librosa.assert_called_once_with(sample_audio_file, sr = 16000)
        speech2text.processor.assert_called_once()
        speech2text.model.generate.assert_called_once()
        speech2text.processor.batch_decode.assert_called_once()
        
        
        
        