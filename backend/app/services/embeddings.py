from typing import List, Text
import logging


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class Embedding:
  
  MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
    
  def __init__(self):
    from sentence_transformers import SentenceTransformer
    self.embedding = SentenceTransformer(self.MODEL_NAME)
    logger.info("Embedding Model Loaded")

def generate_embedding(text: str) -> List[float]:
    raise NotImplementedError("Embedding service not implemented yet")

