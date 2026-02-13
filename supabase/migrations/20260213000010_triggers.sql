-- Migration 10: Triggers
-- Created: 2026-02-13

-- ============================================
-- 1. Auto-update timestamps
-- ============================================

CREATE TRIGGER update_employees_updated_at 
  BEFORE UPDATE ON employees
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at 
  BEFORE UPDATE ON sessions
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audio_recordings_updated_at 
  BEFORE UPDATE ON audio_recordings
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transcriptions_updated_at 
  BEFORE UPDATE ON transcriptions
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at 
  BEFORE UPDATE ON documents
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 2. Session progress auto-update
-- ============================================

CREATE OR REPLACE FUNCTION trigger_update_session_progress()
RETURNS TRIGGER AS $$
BEGIN
  -- Update session progress when audio or document status changes
  IF TG_TABLE_NAME = 'audio_recordings' THEN
    UPDATE sessions 
    SET 
      progress_percentage = calculate_session_progress(NEW.session_id),
      status = CASE 
        WHEN calculate_session_progress(NEW.session_id) = 100 THEN 'completed'
        WHEN calculate_session_progress(NEW.session_id) > 0 THEN 'in_progress'
        ELSE status
      END,
      completed_at = CASE 
        WHEN calculate_session_progress(NEW.session_id) = 100 THEN now()
        ELSE completed_at
      END
    WHERE id = NEW.session_id;
  ELSIF TG_TABLE_NAME = 'documents' THEN
    UPDATE sessions 
    SET 
      progress_percentage = calculate_session_progress(NEW.session_id),
      status = CASE 
        WHEN calculate_session_progress(NEW.session_id) = 100 THEN 'completed'
        WHEN calculate_session_progress(NEW.session_id) > 0 THEN 'in_progress'
        ELSE status
      END,
      completed_at = CASE 
        WHEN calculate_session_progress(NEW.session_id) = 100 THEN now()
        ELSE completed_at
      END
    WHERE id = NEW.session_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audio_processing_progress 
  AFTER INSERT OR UPDATE OF processing_status ON audio_recordings
  FOR EACH ROW 
  EXECUTE FUNCTION trigger_update_session_progress();

CREATE TRIGGER document_processing_progress 
  AFTER INSERT OR UPDATE OF processing_status ON documents
  FOR EACH ROW 
  EXECUTE FUNCTION trigger_update_session_progress();

-- ============================================
-- 3. Processing timestamp tracking
-- ============================================

CREATE OR REPLACE FUNCTION track_processing_times()
RETURNS TRIGGER AS $$
BEGIN
  -- Track when processing starts
  IF OLD.processing_status != 'processing' AND NEW.processing_status = 'processing' THEN
    NEW.processing_started_at = now();
  END IF;
  
  -- Track when processing completes
  IF OLD.processing_status != 'completed' AND NEW.processing_status = 'completed' THEN
    NEW.processing_completed_at = now();
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audio_processing_times 
  BEFORE UPDATE OF processing_status ON audio_recordings
  FOR EACH ROW 
  EXECUTE FUNCTION track_processing_times();

CREATE TRIGGER document_processing_times 
  BEFORE UPDATE OF processing_status ON documents
  FOR EACH ROW 
  EXECUTE FUNCTION track_processing_times();

-- ============================================
-- 4. Session status validation
-- ============================================

CREATE OR REPLACE FUNCTION validate_session_status()
RETURNS TRIGGER AS $$
BEGIN
  -- When starting a session, set started_at
  IF OLD.status != 'in_progress' AND NEW.status = 'in_progress' AND NEW.started_at IS NULL THEN
    NEW.started_at = now();
  END IF;
  
  -- When completing a session, set completed_at
  IF OLD.status != 'completed' AND NEW.status = 'completed' AND NEW.completed_at IS NULL THEN
    NEW.completed_at = now();
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER session_status_validation 
  BEFORE UPDATE OF status ON sessions
  FOR EACH ROW 
  EXECUTE FUNCTION validate_session_status();

COMMENT ON TRIGGER update_employees_updated_at ON employees IS 'Auto-updates updated_at timestamp';
COMMENT ON TRIGGER audio_processing_progress ON audio_recordings IS 'Updates parent session progress';
COMMENT ON TRIGGER audio_processing_times ON audio_recordings IS 'Tracks processing start/end times';