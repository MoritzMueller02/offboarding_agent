CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Quelle (kann Audio oder Document sein)
  source_type TEXT CHECK (source_type IN ('transcription', 'document')) NOT NULL,
  source_id UUID NOT NULL, -- transcription_id oder document_id
  
  -- Chunk-Daten
  chunk_text TEXT NOT NULL,
  chunk_index INTEGER NOT NULL, -- Position im Original
  token_count INTEGER,
  
  -- Embedding
  embedding vector(1536), -- OpenAI ada-002 = 1536 dimensions
  embedding_model TEXT DEFAULT 'textpgmbedding-ada-002',
  
  -- Kontext (wichtig für RAG!)
  context_before TEXT, -- Vorheriger Chunk für Kontext
  context_after TEXT,  -- Nächster Chunk
  
  -- Metadata für Filtering
  metadata JSONB DEFAULT '{}', -- {topic, keywords, speaker, confidence, etc.}
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indizes (KRITISCH für Performance!)
CREATE INDEX idx_chunks_source ON knowledge_chunks(source_type, source_id);
CREATE INDEX idx_chunks_metadata ON knowledge_chunks USING gin(metadata);

-- Vector Search Index (nutzt IVFFlat für schnelle Similarity Search)
CREATE INDEX idx_chunks_embedding ON knowledge_chunks 
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100); -- Tune based on your data size