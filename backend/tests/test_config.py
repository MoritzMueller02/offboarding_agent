import pytest
from pathlib import Path
from backend.app.config import Settings, get_settings
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError


@pytest.fixture(scope = "session")
def mock_settings():
    return Settings(
        _env_file = None, 
        supabase_anon_key="test.key",
        supabase_service_key="test.skey",
        supabase_url="test.url",
        debug = True,
        hf_token= None
        )
    
    
@pytest.mark.unit
def test_imports(mock_settings):
    
    assert mock_settings.supabase_service_key == "test.skey"
    assert mock_settings.supabase_anon_key == "test.key"
    assert mock_settings.supabase_url == "test.url"

    assert mock_settings.debug == True
    assert mock_settings.api_v1_prefix == "/api/v1"
    assert mock_settings.audio_bucket == "audio-recordings"
    assert mock_settings.max_file_size == 50_000_000

@pytest.mark.unit
def test_val_error():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
        supabase_anon_key="test.key",
        supabase_service_key="test.skey",
    )
        
    errors = exc_info.value.errors() 
    assert any(error["loc"] == ("supabase_url",) for error in errors)
    #asert any(error["type"] == "missing" for error in errors)
    
@pytest.mark.integration
def test_max_size_fail():
    with pytest.raises(ValidationError) as exc_info:
            Settings(
        supabase_anon_key="test.key",
        supabase_service_key="test.skey",
        max_file_size=500_000_001,
        )   
    errors = exc_info.value.errors() 
    assert any("max_file_size exceeded" in str(error) for error in errors)