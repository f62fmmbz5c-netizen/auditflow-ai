from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    demo_mode: bool = True
    google_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "asia-east1"
    google_genai_use_vertexai: bool = False
    auditfleet_region: str = "asia-east1"
    auditfleet_require_approval: bool = True
    auditfleet_log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
