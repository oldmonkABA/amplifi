from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Dev mode
    dev_mode: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://amplifi:amplifi@localhost:5432/amplifi"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    google_client_id: str = ""
    google_client_secret: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60 * 24 * 7  # 7 days
    frontend_url: str = "http://localhost:3000"

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    together_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    default_llm_provider: str = "openai"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
