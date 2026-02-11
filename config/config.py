import os
import logging
from pathlib import Path
from dotenv import load_dotenv


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    
    BASE_DIR = Path(__file__).parent.resolve()
    MODELS_DIR = BASE_DIR / "models"
    
    def __init__(self):
        load_dotenv()
        self._setup_evniornment()
        
    def _setup_evniornment(self):
        self.hf_token = os.getenv("HF_TOKEN")
        
        if not self.hf_token:
            logger.warning("HF_TOKEN not found")
            
        self._ensure_directory_exists(self.MODELS_DIR)
        
        os.environ['HF_HOME'] = str(self.MODELS_DIR)
        if self.hf_token:
            os.environ['HF_TOKEN'] = self.hf_token
    
    @staticmethod
    def _ensure_directory_exists(directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Path object representing the directory
        """
        if directory.exists():
            logger.info(f"Directory already exists: {directory}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")