ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_recordings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_chunks ENABLE ROW LEVEL SECURITY;

-- Employees: Nur eigene Daten oder Admin
CREATE POLICY "Users can view own employee data" ON employees
  FOR SELECT
  USING (auth.uid() = auth_user_id OR auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can update own employee data" ON employees
  FOR UPDATE
  USING (auth.uid() = auth_user_id);

-- Sessions: Nur eigene Sessions
CREATE POLICY "Users can view own sessions" ON sessions
  FOR SELECT
  USING (
    employee_id IN (SELECT id FROM employees WHERE auth_user_id = auth.uid())
  );

-- Knowledge Chunks: Alle authenticated users können lesen (Wissensaustausch!)
CREATE POLICY "Authenticated users can read knowledge" ON knowledge_chunks
  FOR SELECT
  TO authenticated
  USING (true);

-- Aber nur Besitzer können erstellen/updaten
CREATE POLICY "Users can insert own knowledge" ON knowledge_chunks
  FOR INSERT
  WITH CHECK (
    source_id IN (
      SELECT t.id FROM transcriptions t
      JOIN audio_recordings ar ON ar.id = t.audio_recording_id
      JOIN sessions s ON s.id = ar.session_id
      JOIN employees e ON e.id = s.employee_id
      WHERE e.auth_user_id = auth.uid()
    )
    OR
    source_id IN (
      SELECT d.id FROM documents d
      JOIN sessions s ON s.id = d.session_id
      JOIN employees e ON e.id = s.employee_id
      WHERE e.auth_user_id = auth.uid()
    )
  );