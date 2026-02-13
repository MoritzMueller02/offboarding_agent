-- Migration 09: Helper functions
-- Created: 2026-02-13

-- ============================================
-- 1. Auto-update timestamp function
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS 'Auto-updates updated_at on row changes';

-- ============================================
-- 2. Session progress calculation
-- ============================================
CREATE OR REPLACE FUNCTION calculate_session_progress(session_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  total_items INTEGER;
  completed_items INTEGER;
  progress INTEGER;
BEGIN
  -- Count total audio recordings + documents
  SELECT 
    COUNT(*) 
  INTO total_items
  FROM (
    SELECT id FROM audio_recordings WHERE session_id = session_uuid
    UNION ALL
    SELECT id FROM documents WHERE session_id = session_uuid
  ) items;
  
  -- Count completed items
  SELECT 
    COUNT(*) 
  INTO completed_items
  FROM (
    SELECT id FROM audio_recordings 
    WHERE session_id = session_uuid AND processing_status = 'completed'
    UNION ALL
    SELECT id FROM documents 
    WHERE session_id = session_uuid AND processing_status = 'completed'
  ) completed;
  
  -- Calculate percentage
  IF total_items > 0 THEN
    progress := (completed_items * 100) / total_items;
  ELSE
    progress := 0;
  END IF;
  
  RETURN progress;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_session_progress IS 'Calculates session progress from audio + docs';

-- ============================================
-- 3. Vector similarity search
-- ============================================
CREATE OR REPLACE FUNCTION search_knowledge(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10,
  filter_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
  chunk_id uuid,
  chunk_text text,
  similarity float,
  metadata jsonb,
  source_type text,
  source_id uuid
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    kc.id,
    kc.chunk_text,
    1 - (kc.embedding <=> query_embedding) as similarity,
    kc.metadata,
    kc.source_type,
    kc.source_id
  FROM knowledge_chunks kc
  WHERE 
    kc.embedding IS NOT NULL
    AND 1 - (kc.embedding <=> query_embedding) > match_threshold
    AND (filter_metadata = '{}'::jsonb OR kc.metadata @> filter_metadata)
  ORDER BY kc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION search_knowledge IS 'Vector similarity search with metadata filtering';

-- ============================================
-- 4. Hybrid search (keyword + vector)
-- ============================================
CREATE OR REPLACE FUNCTION hybrid_search(
  query_text text,
  query_embedding vector(1536),
  match_count int DEFAULT 10,
  keyword_weight float DEFAULT 0.3,
  vector_weight float DEFAULT 0.7
)
RETURNS TABLE (
  chunk_id uuid,
  chunk_text text,
  combined_score float,
  keyword_score float,
  vector_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH keyword_search AS (
    SELECT 
      id,
      chunk_text,
      ts_rank(
        to_tsvector('english', chunk_text), 
        plainto_tsquery('english', query_text)
      ) as k_score
    FROM knowledge_chunks
    WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', query_text)
  ),
  vector_search AS (
    SELECT 
      id,
      chunk_text,
      1 - (embedding <=> query_embedding) as v_score
    FROM knowledge_chunks
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count * 2
  )
  SELECT 
    COALESCE(k.id, v.id) as chunk_id,
    COALESCE(k.chunk_text, v.chunk_text) as chunk_text,
    (COALESCE(k.k_score, 0) * keyword_weight + COALESCE(v.v_score, 0) * vector_weight) as combined_score,
    COALESCE(k.k_score, 0) as keyword_score,
    COALESCE(v.v_score, 0) as vector_score
  FROM keyword_search k
  FULL OUTER JOIN vector_search v ON k.id = v.id
  ORDER BY combined_score DESC
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION hybrid_search IS 'Combines keyword and vector search with configurable weights';

-- ============================================
-- 5. Get session statistics
-- ============================================
CREATE OR REPLACE FUNCTION get_session_stats(session_uuid UUID)
RETURNS TABLE (
  session_id uuid,
  audio_count bigint,
  document_count bigint,
  total_duration_seconds bigint,
  knowledge_chunk_count bigint,
  avg_confidence float
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    s.id,
    COUNT(DISTINCT ar.id) as audio_count,
    COUNT(DISTINCT d.id) as document_count,
    COALESCE(SUM(ar.duration_seconds), 0) as total_duration_seconds,
    COUNT(DISTINCT kc.id) as knowledge_chunk_count,
    AVG(t.confidence_score) as avg_confidence
  FROM sessions s
  LEFT JOIN audio_recordings ar ON ar.session_id = s.id
  LEFT JOIN documents d ON d.session_id = s.id
  LEFT JOIN transcriptions t ON t.audio_recording_id = ar.id
  LEFT JOIN knowledge_chunks kc ON (
    (kc.source_type = 'transcription' AND kc.source_id = t.id) OR
    (kc.source_type = 'document' AND kc.source_id = d.id)
  )
  WHERE s.id = session_uuid
  GROUP BY s.id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_session_stats IS 'Aggregates session statistics for dashboards';