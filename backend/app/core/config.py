from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart AI Business Assistant"
    # No default — must be provided via DATABASE_URL environment variable on Render.
    # A missing value will raise a clear ValidationError at startup instead of
    # silently attempting to connect to an unreachable Docker Compose hostname.
    database_url: str
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

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


settings = Settings()

# Normalize scheme: Render / Supabase supply 'postgresql://' but asyncpg needs
# 'postgresql+asyncpg://'.
if "+asyncpg" not in settings.database_url and settings.database_url.startswith("postgresql://"):
    settings.database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg does not accept 'sslmode' — replace with 'ssl' so the driver honours it.
if "sslmode=" in settings.database_url:
    settings.database_url = settings.database_url.replace("sslmode=", "ssl=")
