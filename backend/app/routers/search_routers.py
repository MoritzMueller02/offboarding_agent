from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from uuid import UUID

from app.dependencies import get_db
from app.db.repositories.knowledge_chunks_repository import KnowledgeChunkRepository
from app.models.schema import SearchRequest, SearchResponse, SearchResult
from app.services.embeddings import generate_embedding

router = APIRouter()


@router.post("/", response_model=SearchResponse)
def search_knowledge(payload: SearchRequest, db: Client = Depends(get_db)):
    """
    Search knowledge chunks using vector similarity.
    Requires the `match_chunks` SQL function in Supabase and a configured embedding service.
    """
    try:
        embedding = generate_embedding(payload.query)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    source_type_filter = payload.filters.get("source_type") if payload.filters else None

    repo = KnowledgeChunkRepository(db)
    raw_results = repo.search_similar(
        embedding=embedding,
        limit=payload.limit,
        source_type=source_type_filter,
    )

    results = [
        SearchResult(
            chunk_id=UUID(r["chunk_id"]),
            chunk_text=r["chunk_text"],
            similarity=r["similarity"],
            metadata=r.get("metadata") or {},
            source_type=r["source_type"],
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=payload.query,
        results=results,
        count=len(results),
    )
