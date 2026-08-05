from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Document RAG Backend"
    debug: bool = True

    # GROQ
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Database
    database_url: str

    # Redis
    redis_host: str
    redis_port: int

    # Qdrant
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str

    # Embedding
    embedding_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()