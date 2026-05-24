from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart AI Business Assistant"
    # No default — must be provided via DATABASE_URL environment variable on Render.
    # A missing value will raise a clear ValidationError at startup instead of
    # silently attempting to connect to an unreachable Docker Compose hostname.
    database_url: str = Field(..., env=("DATABASE_URL", "database_url"))

    jwt_secret: str = Field(
        default="change-me",
        env=("JWT_SECRET", "SECRET_KEY", "jwt_secret"),
    )
    jwt_algorithm: str = Field(
        default="HS256",
        env=("JWT_ALGORITHM", "ALGORITHM", "jwt_algorithm"),
    )
    access_token_expire_minutes: int = 60
    chroma_path: str = Field(default="./chroma_store_v1", env=("CHROMA_PATH", "chroma_path"))
    frontend_dir: str = Field(default="../frontend", env=("FRONTEND_DIR", "frontend_dir"))
    allow_origins: str = Field(
        default="http://localhost:5173,http://localhost:8000,http://localhost:8080,https://smart-ai-business-assistant-platform.vercel.app,https://smart-ai-business-assistant-platfor.vercel.app",
        env=("ALLOW_ORIGINS", "allow_origins"),
    )
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
