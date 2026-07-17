from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "sw1-be-fastapi"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.4-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    TEMPERATURE: float = 0.3

    # Internal auth
    INTERNAL_API_KEY: str = "sw1-internal-secret"

    # Server
    PORT: int = 8028

    # Ciclo 2 — Routing model
    ROUTING_MODEL_PATH: str = "/app/models/routing_model.h5"

    # Ciclo 2 — Whisper model size (tiny, base, small, medium, large)
    WHISPER_MODEL_SIZE: str = "base"


settings = Settings()
