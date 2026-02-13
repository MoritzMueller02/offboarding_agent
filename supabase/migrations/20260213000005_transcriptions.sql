CREATE TABLE transcriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Beziehungen
  audio_recording_id UUID NOT NULL REFERENCES audio_recordings(id) ON DELETE CASCADE,
  
  -- Transkriptions-Daten
  text TEXT NOT NULL,
  language TEXT DEFAULT 'de',
  
  -- Model-Info
  model_name TEXT, -- z.B. 'whisper-large-v3'
  model_version TEXT,
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  
  -- Timestamps mit Wörtern (optional für präzises Highlighting)
  word_timestamps JSONB, -- [{word, start, end, confidence}]
  
  -- Processing
  processing_time_ms INTEGER,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indizes
CREATE INDEX idx_transcriptions_audio ON transcriptions(audio_recording_id);
CREATE INDEX idx_transcriptions_language ON transcriptions(language);