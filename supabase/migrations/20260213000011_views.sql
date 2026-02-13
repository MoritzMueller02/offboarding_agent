-- Migration 11: Views
-- Created: 2026-02-13

-- ============================================
-- 1. Session Overview (most common query)
-- ============================================
CREATE VIEW session_overview AS
SELECT 
  s.id,
  s.title,
  s.description,
  s.session_type,
  s.status,
  s.progress_percentage,
  s.scheduled_at,
  s.started_at,
  s.completed_at,
  
  -- Employee info
  e.id as employee_id,
  e.first_name || ' ' || e.last_name as employee_name,
  e.email as employee_email,
  e.department,
  e.position,
  
  -- Aggregated stats
  COUNT(DISTINCT ar.id) as audio_count,
  COUNT(DISTINCT d.id) as document_count,
  COUNT(DISTINCT t.id) as transcription_count,
  COUNT(DISTINCT kc.id) as knowledge_chunk_count,
  
  -- Audio metrics
  COALESCE(SUM(ar.duration_seconds), 0) as total_audio_duration,
  AVG(ar.duration_seconds) as avg_audio_duration,
  
  -- Quality metrics
  AVG(t.confidence_score) as avg_transcription_confidence,
  
  -- Processing status summary
  COUNT(DISTINCT ar.id) FILTER (WHERE ar.processing_status = 'completed') as completed_audio,
  COUNT(DISTINCT d.id) FILTER (WHERE d.processing_status = 'completed') as completed_documents,
  
  s.created_at,
  s.updated_at
FROM sessions s
JOIN employees e ON e.id = s.employee_id
LEFT JOIN audio_recordings ar ON ar.session_id = s.id
LEFT JOIN documents d ON d.session_id = s.id
LEFT JOIN transcriptions t ON t.audio_recording_id = ar.id
LEFT JOIN knowledge_chunks kc ON (
  (kc.source_type = 'transcription' AND kc.source_id = t.id) OR
  (kc.source_type = 'document' AND kc.source_id = d.id)
)
GROUP BY 
  s.id, 
  e.id, 
  e.first_name, 
  e.last_name, 
  e.email, 
  e.department, 
  e.position;

COMMENT ON VIEW session_overview IS 'Complete session info with aggregated stats';

-- ============================================
-- 2. Employee Knowledge Summary
-- ============================================
CREATE VIEW employee_knowledge_summary AS
SELECT 
  e.id as employee_id,
  e.first_name || ' ' || e.last_name as employee_name,
  e.department,
  e.position,
  e.employment_status,
  
  -- Session counts
  COUNT(DISTINCT s.id) as total_sessions,
  COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'completed') as completed_sessions,
  
  -- Content metrics
  COUNT(DISTINCT ar.id) as total_audio_recordings,
  SUM(ar.duration_seconds) as total_audio_duration_seconds,
  COUNT(DISTINCT d.id) as total_documents,
  COUNT(DISTINCT kc.id) as total_knowledge_chunks,
  
  -- Latest activity
  MAX(s.completed_at) as last_session_completed,
  
  e.created_at as employee_since
FROM employees e
LEFT JOIN sessions s ON s.employee_id = e.id
LEFT JOIN audio_recordings ar ON ar.session_id = s.id
LEFT JOIN documents d ON d.session_id = s.id
LEFT JOIN transcriptions t ON t.audio_recording_id = ar.id
LEFT JOIN knowledge_chunks kc ON (
  (kc.source_type = 'transcription' AND kc.source_id = t.id) OR
  (kc.source_type = 'document' AND kc.source_id = d.id)
)
GROUP BY 
  e.id, 
  e.first_name, 
  e.last_name, 
  e.department, 
  e.position, 
  e.employment_status,
  e.created_at;

COMMENT ON VIEW employee_knowledge_summary IS 'Knowledge contribution per employee';

-- ============================================
-- 3. Processing Pipeline Status
-- ============================================
CREATE VIEW processing_pipeline_status AS
SELECT 
  'audio' as content_type,
  processing_status,
  COUNT(*) as count,
  SUM(file_size) as total_size_bytes,
  AVG(duration_seconds) as avg_duration_seconds,
  MIN(created_at) as oldest_item,
  MAX(created_at) as newest_item
FROM audio_recordings
GROUP BY processing_status

UNION ALL

SELECT 
  'document' as content_type,
  processing_status,
  COUNT(*) as count,
  SUM(file_size) as total_size_bytes,
  NULL as avg_duration_seconds,
  MIN(created_at) as oldest_item,
  MAX(created_at) as newest_item
FROM documents
GROUP BY processing_status

ORDER BY content_type, processing_status;

COMMENT ON VIEW processing_pipeline_status IS 'Real-time processing queue status';

-- ============================================
-- 4. Knowledge Base Statistics
-- ============================================
CREATE VIEW knowledge_base_stats AS
SELECT 
  source_type,
  COUNT(*) as total_chunks,
  AVG(LENGTH(chunk_text)) as avg_chunk_length,
  SUM(token_count) as total_tokens,
  COUNT(DISTINCT source_id) as unique_sources,
  
  -- Metadata analysis
  COUNT(*) FILTER (WHERE metadata ? 'department') as chunks_with_department,
  COUNT(*) FILTER (WHERE metadata ? 'topics') as chunks_with_topics,
  COUNT(*) FILTER (WHERE embedding IS NOT NULL) as chunks_with_embeddings,
  
  MIN(created_at) as oldest_chunk,
  MAX(created_at) as newest_chunk
FROM knowledge_chunks
GROUP BY source_type;

COMMENT ON VIEW knowledge_base_stats IS 'Knowledge base health metrics';

-- ============================================
-- 5. Recent Activity Feed
-- ============================================
CREATE VIEW recent_activity AS
SELECT 
  'session_created' as activity_type,
  s.id as activity_id,
  s.created_at as activity_time,
  e.first_name || ' ' || e.last_name as actor,
  'Created session: ' || s.title as description,
  jsonb_build_object(
    'session_id', s.id,
    'employee_id', e.id,
    'session_type', s.session_type
  ) as metadata
FROM sessions s
JOIN employees e ON e.id = s.employee_id

UNION ALL

SELECT 
  'audio_uploaded' as activity_type,
  ar.id as activity_id,
  ar.created_at as activity_time,
  e.first_name || ' ' || e.last_name as actor,
  'Uploaded audio: ' || ar.file_name as description,
  jsonb_build_object(
    'audio_id', ar.id,
    'session_id', ar.session_id,
    'duration_seconds', ar.duration_seconds
  ) as metadata
FROM audio_recordings ar
JOIN sessions s ON s.id = ar.session_id
JOIN employees e ON e.id = s.employee_id

UNION ALL

SELECT 
  'document_uploaded' as activity_type,
  d.id as activity_id,
  d.created_at as activity_time,
  e.first_name || ' ' || e.last_name as actor,
  'Uploaded document: ' || d.file_name as description,
  jsonb_build_object(
    'document_id', d.id,
    'session_id', d.session_id,
    'document_type', d.document_type
  ) as metadata
FROM documents d
JOIN sessions s ON s.id = d.session_id
JOIN employees e ON e.id = s.employee_id

ORDER BY activity_time DESC
LIMIT 100;

COMMENT ON VIEW recent_activity IS 'Activity feed for dashboard';