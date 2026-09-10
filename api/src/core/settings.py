from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    database_url: str
    minio_url: str
    minio_user: str
    minio_password: str
    minio_secure: bool

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_ROOT}/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()