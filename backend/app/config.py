# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path
from functools import lru_cache
import os

ROOT_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """
    Application settings with validation.
    Combines your ML setup with API config.
    """
    
    # Paths (dein Ansatz, aber als Pydantic Field)
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve())
    
    @property
    def models_dir(self) -> Path:
        """Computed property for models directory""" # aufrufen ohne klammer
        return self.base_dir / "models"
    
    hf_token: str | None = None
    hf_home: str | None = None
    
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    audio_bucket: str = "audio-recordings"
    max_file_size: int = 50_000_000  # 50 MB
    
    @field_validator("max_file_size")
    def validate_file_sie(cls,v):
        if v > 500_000_000:
            raise ValueError("max_file_size exceeded")
        return v
        
    
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # Pydantic Config
    model_config = {
        "env_file": str(ROOT_DIR/".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    def setup_huggingface(self):
        """Your original setup logic"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        if self.hf_home:
            os.environ['HF_HOME'] = self.hf_home
        else:
            os.environ['HF_HOME'] = str(self.models_dir)
            
        if self.hf_token:
            os.environ['HF_TOKEN'] = self.hf_token
            

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.setup_huggingface()  # Call your setup
    return settings