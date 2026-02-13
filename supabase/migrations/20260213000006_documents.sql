CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Beziehungen
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  
  -- Storage
  storage_bucket TEXT NOT NULL DEFAULT 'documents',
  storage_path TEXT NOT NULL UNIQUE,
  
  -- Metadaten
  file_name TEXT NOT NULL,
  file_size BIGINT,
  mime_type TEXT,
  document_type TEXT CHECK (document_type IN ('pdf', 'docx', 'txt', 'markdown', 'presentation', 'spreadsheet', 'other')),
  
  -- Processing
  processing_status TEXT CHECK (processing_status IN ('uploaded', 'queued', 'extracting', 'completed', 'failed')) DEFAULT 'uploaded',
  extracted_text TEXT,
  page_count INTEGER,
  error_message TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);