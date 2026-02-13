CREATE TABLE knowledge_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Wer fragt?
  user_id UUID REFERENCES auth.users(id),
  
  -- Query
  query_text TEXT NOT NULL,
  query_embedding vector(1536),
  
  -- Filter
  filters JSONB, -- {department, date_range, topics, etc.}
  
  -- Ergebnisse
  result_count INTEGER,
  top_chunk_ids UUID[], -- Array der zurückgegebenen Chunk-IDs
  
  -- Performance
  search_time_ms INTEGER,
  
  -- Feedback (optional)
  user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
  feedback TEXT,
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_queries_user ON knowledge_queries(user_id);
CREATE INDEX idx_queries_created ON knowledge_queries(created_at);