from typing import List


def generate_embedding(text: str) -> List[float]:
    """
    Generate a vector embedding for the given text.

    TODO: Implement with your chosen embedding model, e.g.:
      - OpenAI:  openai.embeddings.create(input=text, model="text-embedding-ada-002")
      - Local:   sentence_transformers.SentenceTransformer("all-MiniLM-L6-v2").encode(text)
      - HF API:  requests.post(HF_ENDPOINT, json={"inputs": text})

    The output must match the vector dimension defined in the DB (currently 1536 for ada-002).
    """
    raise NotImplementedError(
        "Embedding service not implemented. "
        "Add your embedding model in backend/app/services/embeddings.py"
    )
