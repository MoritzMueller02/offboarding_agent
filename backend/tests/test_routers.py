"""
Router tests using FastAPI's TestClient.

Wir mocken die Supabase-DB damit keine echte Verbindung nötig ist.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app
from app.dependencies import get_db


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_db():
    """Gibt eine gefakte Supabase-DB zurück."""
    return Mock()


@pytest.fixture
def client(mock_db):
    """
    TestClient mit überschriebener get_db-Dependency.
    FastAPI erlaubt es, Dependencies für Tests zu ersetzen.
    """
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()  # nach dem Test aufräumen


def db_returns(mock_db, data: list):
    """Hilfsfunktion: setzt was die Mock-DB zurückgibt."""
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = data


# ============================================================
# Employee Router Tests
# ============================================================

class TestEmployeeRouter:

    def test_get_employee_not_found(self, client, mock_db):
        db_returns(mock_db, [])  # DB gibt nichts zurück

        response = client.get(f"/api/v1/employees/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Employee not found"

    def test_get_employee_found(self, client, mock_db):
        employee_id = uuid4()
        db_returns(mock_db, [{
            "id": str(employee_id),
            "email": "max@example.com",
            "first_name": "Max",
            "last_name": "Mustermann",
            "employment_status": "active",
            "department": None,
            "position": None,
            "employee_id": None,
            "offboarding_date": None,
            "last_working_day": None,
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }])

        response = client.get(f"/api/v1/employees/{employee_id}")

        assert response.status_code == 200
        assert response.json()["email"] == "max@example.com"

    def test_get_employees_invalid_status(self, client):
        response = client.get("/api/v1/employees/status/ungültig")

        assert response.status_code == 422


# ============================================================
# Session Router Tests
# ============================================================

class TestSessionRouter:

    def test_get_session_not_found(self, client, mock_db):
        db_returns(mock_db, [])

        response = client.get(f"/api/v1/sessions/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    def test_create_session_invalid_type(self, client):
        """session_type muss einem erlaubten Wert entsprechen."""
        response = client.post("/api/v1/sessions/", json={
            "title": "Test Session",
            "session_type": "falscher_typ",
            "employee_id": str(uuid4()),
        })

        assert response.status_code == 422  # Pydantic validation error


# ============================================================
# Audio Router Tests
# ============================================================

class TestAudioRouter:

    def test_upload_wrong_mime_type(self, client):
        """PDFs sind keine Audiodateien → 415."""
        response = client.post(
            "/api/v1/audio/upload",
            data={"session_id": str(uuid4())},
            files={"file": ("test.pdf", b"fake content", "application/pdf")},
        )

        assert response.status_code == 415

    def test_upload_file_too_large(self, client):
        """Dateien über 50 MB werden abgelehnt → 413."""
        big_file = b"x" * 50_000_001

        response = client.post(
            "/api/v1/audio/upload",
            data={"session_id": str(uuid4())},
            files={"file": ("test.mp3", big_file, "audio/mpeg")},
        )

        assert response.status_code == 413

    def test_get_recording_not_found(self, client, mock_db):
        db_returns(mock_db, [])

        response = client.get(f"/api/v1/audio/{uuid4()}")

        assert response.status_code == 404


# ============================================================
# Transcription Router Tests
# ============================================================

class TestTranscriptionRouter:
    
    def test_transcription_not_found(self, client, mock_db):
        db_returns(mock_db, [])
        
        response = client.get(f"/api/v1/transcriptions/{uuid4()}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Transcription not found"
        
        
    def test_transcription_found(self, client, mock_db):
        transcription_id = uuid4()
        db_returns(mock_db, [{
            "transcription_id" : transcription_id,
            "audio_recording_id" : transcription_id,
            "text": "abbb",
            "language" : None,
            "confidence_score" : None
        }])
        
        response = client.get(f"/api/v1/transcriptions/{transcription_id}")
        
        assert response.status_code == 200
        assert response.json()["text"] == "abbb"

        