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

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    MAX_TOKENS: int = 800
    TEMPERATURE: float = 0.7

    # Internal auth
    INTERNAL_API_KEY: str = "sw1-internal-secret"

    # Server
    PORT: int = 8001


settings = Settings()
