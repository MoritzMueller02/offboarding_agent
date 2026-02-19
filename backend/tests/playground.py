from app.config import Settings, get_settings

settings = Settings(
    hf_token=None,
    debug= False,
    api_v1_prefix= "/api/v1",
    audio_bucket = "audio-recordings",
    max_file_size = 50000000,
)

print(settings)