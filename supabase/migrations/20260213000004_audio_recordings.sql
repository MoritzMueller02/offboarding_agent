CREATE TABLE audio_recordings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Beziehungen
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  
  -- File Storage (Supabase Storage)
  storage_bucket TEXT NOT NULL DEFAULT 'audio-recordings',
  storage_path TEXT NOT NULL UNIQUE,
  
  -- Metadaten
  file_name TEXT NOT NULL,
  file_size BIGINT, -- in Bytes
  mime_type TEXT,
  duration_seconds INTEGER,
  
  -- Processing Status
  processing_status TEXT CHECK (processing_status IN ('uploaded', 'queued', 'processing', 'completed', 'failed')) DEFAULT 'uploaded',
  error_message TEXT,
  
  -- Qualität
  audio_quality TEXT CHECK (audio_quality IN ('low', 'medium', 'high')),
  sample_rate INTEGER,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indizes
CREATE INDEX idx_audio_session ON audio_recordings(session_id);
CREATE INDEX idx_audio_status ON audio_recordings(processing_status);
CREATE INDEX idx_audio_storage_path ON audio_recordings(storage_path);