from config.config import Config
from src.audio_processing.speech2text import Speech2Text


config = Config()

config._ensure_directory_exists(config.BASE_DIR)