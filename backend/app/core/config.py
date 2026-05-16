from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart AI Business Assistant"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/smart_assistant"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    chroma_path: str = "./chroma_store"
    frontend_dir: str = "../frontend"
    allow_origins: str = "http://localhost:5173,http://localhost:8000,http://localhost:8080"
    llm_mode: str = "local"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_seconds: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# If a deploy platform (Render, Supabase) provides a DATABASE_URL like
# 'postgresql://user:pass@host:port/db', SQLAlchemy async engine will try to
# import a sync DBAPI (psycopg2). Ensure the async driver is used by
# normalizing the scheme to 'postgresql+asyncpg://' when '+asyncpg' is missing.
if settings.database_url.startswith("postgresql://") and "+asyncpg" not in settings.database_url:
    settings.database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
