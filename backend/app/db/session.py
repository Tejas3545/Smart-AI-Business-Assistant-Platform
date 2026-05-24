from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

from sqlalchemy.pool import NullPool

engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
    # Both dialect-level and driver-level disables for PgBouncer / Supabase compatibility.
    prepared_statement_cache_size=0,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
