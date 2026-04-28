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
    OPENAI_MODEL: str = "gpt-5.4-mini"
    TEMPERATURE: float = 0.3

    # Internal auth
    INTERNAL_API_KEY: str = "sw1-internal-secret"

    # Server
    PORT: int = 8028


settings = Settings()
