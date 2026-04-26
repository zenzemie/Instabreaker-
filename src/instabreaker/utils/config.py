import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    openai_api_key: str | None = None
    app_dir: Path = Path.home() / ".instabreaker"
    sessions_dir: Path = Path.home() / ".instabreaker" / "sessions"
    checkpoints_dir: Path = Path.home() / ".instabreaker" / "checkpoints"
    default_timeout: int = 30
    max_retries: int = 3
    
    def __init__(self, **values):
        super().__init__(**values)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
