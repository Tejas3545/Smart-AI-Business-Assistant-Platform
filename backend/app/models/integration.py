from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "gmail", "webhook", "slack", "crm_hubspot"
    status: Mapped[str] = mapped_column(String(20), default="active")
    credentials: Mapped[dict] = mapped_column(JSON, default=dict) # API keys, tokens, webhook urls
    config: Mapped[dict] = mapped_column(JSON, default=dict) # extra settings
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
