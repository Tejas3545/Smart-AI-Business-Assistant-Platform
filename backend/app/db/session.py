from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

db_url = str(settings.database_url)
if "?" in db_url:
    if "prepared_statement_cache_size" not in db_url:
        db_url += "&prepared_statement_cache_size=0"
else:
    db_url += "?prepared_statement_cache_size=0"

engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,  # Recycle connections every 30 min (Render closes idle ones)
    pool_size=5,
    connect_args={"statement_cache_size": 0},
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
