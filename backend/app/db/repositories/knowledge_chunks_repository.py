from typing import Optional, List, Dict, Literal, Any
from uuid import UUID
from supabase import Client


class KnowledgeChunkRepository:

    def __init__(self, db: Client):
        self.db = db
        self.table_name = "knowledge_chunks"

    def create(
        self,
        source_type: Literal['transcription', 'document'],
        source_id: UUID,
        chunk_text: str,
        chunk_index: int,
        embedding: Optional[List[float]] = None,
        embedding_model: Optional[str] = None,
        token_count: Optional[int] = None,
        context_before: Optional[str] = None,
        context_after: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Save a knowledge chunk with optional vector embedding."""
        data: Dict[str, Any] = {
            "source_type": source_type,
            "source_id": str(source_id),
            "chunk_text": chunk_text,
            "chunk_index": chunk_index,
        }

        if embedding is not None:
            data["embedding"] = embedding
        if embedding_model is not None:
            data["embedding_model"] = embedding_model
        if token_count is not None:
            data["token_count"] = token_count
        if context_before is not None:
            data["context_before"] = context_before
        if context_after is not None:
            data["context_after"] = context_after
        if metadata is not None:
            data["metadata"] = metadata

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("id", str(id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def list_by_source(
        self,
        source_type: Literal['transcription', 'document'],
        source_id: UUID,
    ) -> List[Dict[str, Any]]:
        """List all chunks for a given source, ordered by position."""
        result = (
            self.db.table(self.table_name)
            .select("*")
            .eq("source_type", source_type)
            .eq("source_id", str(source_id))
            .order("chunk_index")
            .execute()
        )
        return result.data

    def search_similar(
        self,
        embedding: List[float],
        limit: int = 10,
        match_threshold: float = 0.7,
        source_type: Optional[Literal['transcription', 'document']] = None,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search via the `search_knowledge` Supabase RPC (pgvector cosine distance).

        Defined in migration 20260213000009_functions.sql.
        source_type is filtered client-side since the RPC filters only on the metadata JSONB column.
        """
        params: Dict[str, Any] = {
            "query_embedding": embedding,
            "match_count": limit,
            "match_threshold": match_threshold,
            "filter_metadata": {},
        }

        result = self.db.rpc("search_knowledge", params).execute()
        data = result.data

        if source_type:
            data = [r for r in data if r.get("source_type") == source_type]

        return data
