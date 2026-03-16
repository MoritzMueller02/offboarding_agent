from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
from pathlib import Path
import librosa
import logging
import io


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class Speech2Text:

    MODEL_NAME = "facebook/s2t-small-librispeech-asr"
    SAMPLE_RATE = 16000
    
    def __init__(self):
        self.model = Speech2TextForConditionalGeneration.from_pretrained(self.MODEL_NAME)
        self.processor = Speech2TextProcessor.from_pretrained(self.MODEL_NAME)
        logging.info("Models initiated")
        
    
    def prepare_audio(self, audio_bytes: bytes):
        buffer = io.BytesIO(audio_bytes)        
        audio_array, sr = librosa.load(buffer, sr = 16000)
        return audio_array, sr
        
    def transcribe_audio(self, audio_bytes: bytes):
        import torch
        audio_array, sr = self.prepare_audio(audio_bytes)
        inputs = self.processor(audio_array, sampling_rate = sr, return_tensors = "pt")
        generated_ids = self.model.generate(inputs["input_features"], attention_mask=inputs["attention_mask"])
        transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        result = transcription[0]
    
        logger.info(f"Transcription complete: {result}")
        return result


    