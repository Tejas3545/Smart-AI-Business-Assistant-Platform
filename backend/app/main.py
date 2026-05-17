from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import analytics, auth, chat, docs, leads, workflows
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401

setup_logging()


from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: apply schema migrations and create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Run raw migrations to fix schema drifts on existing tables
        migrations = [
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS tokens INTEGER DEFAULT 0 NOT NULL;",
            "ALTER TABLE conversations ALTER COLUMN title DROP NOT NULL;",
            "ALTER TABLE audit_logs ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE conversations ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE documents ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE leads ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE messages ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE user_memories ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;",
            "ALTER TABLE workflow_runs ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;"
        ]
        for query in migrations:
            try:
                await conn.execute(text(query))
            except Exception as e:
                # Ignore errors if columns already cast or tables don't exist
                pass

    yield
    # Shutdown: dispose the engine pool
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = [origin.strip().rstrip("/") for origin in settings.allow_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ensure CORS headers are present even on unhandled 500 errors.

    FastAPI's CORSMiddleware only wraps successful responses; if an exception
    propagates before a response is built the middleware is bypassed and the
    browser sees a CORS violation instead of the actual error.
    """
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in origins or "*" in origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}"},
        headers=headers,
    )


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(docs.router, prefix="/api/docs", tags=["docs"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

frontend_path = (Path(__file__).parent / settings.frontend_dir).resolve()
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
