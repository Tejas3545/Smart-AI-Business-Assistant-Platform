from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import analytics, auth, chat, docs, leads, workflows
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose the engine pool
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

origins = [origin.strip() for origin in settings.allow_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
