from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import analytics, auth, chat, docs, leads, workflows, integrations, admin
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401

setup_logging()
logger = logging.getLogger(__name__)


from sqlalchemy import text


async def _table_exists(table_name: str) -> bool:
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=:table_name)"),
            {"table_name": table_name},
        )
        return bool(result.scalar())


async def _column_exists(table_name: str, column_name: str) -> bool:
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name=:table_name AND column_name=:column_name)"
            ),
            {"table_name": table_name, "column_name": column_name},
        )
        return bool(result.scalar())


async def _run_sql_safe(query: str) -> None:
    try:
        async with engine.begin() as conn:
            await conn.execute(text(query))
    except Exception as exc:
        logger.warning("Startup migration skipped: %s | error=%s", query, exc)


async def _run_schema_repair_migrations() -> None:
    if await _table_exists("users"):
        if not await _column_exists("users", "workspace_id"):
            await _run_sql_safe("ALTER TABLE users ADD COLUMN workspace_id INTEGER;")

    await _run_sql_safe("ALTER TABLE messages ADD COLUMN IF NOT EXISTS tokens INTEGER DEFAULT 0 NOT NULL;")
    await _run_sql_safe("ALTER TABLE conversations ALTER COLUMN title DROP NOT NULL;")

    # Normalize legacy table naming if older DB has user_memories.
    has_user_memory = await _table_exists("user_memory")
    has_user_memories = await _table_exists("user_memories")
    if not has_user_memory and has_user_memories:
        await _run_sql_safe("ALTER TABLE user_memories RENAME TO user_memory;")

    # Normalize timestamp tz drifts for known tables.
    for table_name in [
        "audit_logs",
        "conversations",
        "documents",
        "leads",
        "messages",
        "user_memory",
        "users",
        "workflow_runs",
    ]:
        if await _table_exists(table_name) and await _column_exists(table_name, "created_at"):
            await _run_sql_safe(
                f"ALTER TABLE {table_name} ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::timestamp;"
            )

    # Normalize lead-related constraints for legacy schemas.
    if await _table_exists("leads"):
        if await _column_exists("leads", "score"):
            await _run_sql_safe("ALTER TABLE leads ALTER COLUMN score SET DEFAULT 0;")
            await _run_sql_safe("UPDATE leads SET score = 0 WHERE score IS NULL;")
            await _run_sql_safe("ALTER TABLE leads ALTER COLUMN score SET NOT NULL;")
        if await _column_exists("leads", "status"):
            await _run_sql_safe("ALTER TABLE leads ALTER COLUMN status SET DEFAULT 'cold';")
            await _run_sql_safe("UPDATE leads SET status = 'cold' WHERE status IS NULL OR status = '';")
            await _run_sql_safe("ALTER TABLE leads ALTER COLUMN status SET NOT NULL;")
        if await _column_exists("leads", "name"):
            await _run_sql_safe("ALTER TABLE leads ALTER COLUMN name SET NOT NULL;")


def _check_rag_runtime_readiness() -> None:
    try:
        import chromadb  # noqa: F401
        import numpy  # noqa: F401
        logger.info("RAG runtime check passed: chromadb and numpy available.")
    except Exception as exc:
        logger.error("RAG runtime check failed: %s", exc)


import asyncio
from app.services.automation import automation_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _run_schema_repair_migrations()
    _check_rag_runtime_readiness()

    # Start background automation worker
    worker_task = asyncio.create_task(automation_worker())

    yield
    # Shutdown: dispose the engine pool
    worker_task.cancel()
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = [
    "http://localhost:8080",
    "https://smart-ai-business-assistant-platform.onrender.com",
    "https://smart-ai-business-assistant-platfor.vercel.app",
]

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
        content={"detail": f"Internal server error: {type(exc).__name__} - {str(exc)}"},
        headers=headers,
    )


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(docs.router, prefix="/api/docs", tags=["docs"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

frontend_path = (Path(__file__).parent / settings.frontend_dir).resolve()
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    @app.get("/")
    async def root() -> dict:
        return {"status": "ok", "service": settings.app_name, "health": "/api/health"}


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
