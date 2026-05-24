from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "lead_created", "webhook_received"
    trigger_config: Mapped[dict] = mapped_column(JSON, default=dict)
    nodes: Mapped[list] = mapped_column(JSON, default=list) # the diagram/flow of actions and conditions
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class AutomationTask(Base):
    __tablename__ = "automation_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id"), nullable=False)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflows.id"), nullable=True)
    trigger_source: Mapped[str] = mapped_column(String(100), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default={})
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, processing, completed, failed, retrying
    step_index: Mapped[int] = mapped_column(Integer, default=0) # which node in workflow
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    error_log: Mapped[str] = mapped_column(Text, nullable=True)
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
