from typing import List
import logging


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class Embedding:

  MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

  def __init__(self):
    from sentence_transformers import SentenceTransformer
    self.embedding = SentenceTransformer(self.MODEL_NAME)
    logger.info("Embedding Model Loaded")

  def generate_embedding(self, text: str) -> List[float]:
    return self.embedding.encode(text)


_embedding_service = None

def get_embedding_service() -> Embedding:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = Embedding()
    return _embedding_service