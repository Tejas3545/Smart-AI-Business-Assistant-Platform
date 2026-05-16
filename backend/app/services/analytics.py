from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.document import Document
from app.models.lead import Lead
from app.models.message import Message
from app.models.workflow import WorkflowRun
from app.models.audit import AuditLog


async def get_summary(db: AsyncSession) -> dict:
    total_conversations = await db.scalar(select(func.count(Conversation.id)))
    total_messages = await db.scalar(select(func.count(Message.id)))
    total_leads = await db.scalar(select(func.count(Lead.id)))
    hot_leads = await db.scalar(select(func.count(Lead.id)).where(Lead.status == "hot"))
    workflow_runs = await db.scalar(select(func.count(WorkflowRun.id)))
    documents_uploaded = await db.scalar(select(func.count(Document.id)))
    total_user_tokens = await db.scalar(select(func.coalesce(func.sum(Message.tokens), 0)).where(Message.role == "user"))
    total_ai_tokens = await db.scalar(select(func.coalesce(func.sum(Message.tokens), 0)).where(Message.role == "assistant"))

    return {
        "total_conversations": total_conversations or 0,
        "total_messages": total_messages or 0,
        "total_leads": total_leads or 0,
        "hot_leads": hot_leads or 0,
        "workflow_runs": workflow_runs or 0,
        "documents_uploaded": documents_uploaded or 0,
        "total_user_tokens": total_user_tokens or 0,
        "total_ai_tokens": total_ai_tokens or 0,
    }


async def get_recent_audit_logs(db: AsyncSession, limit: int = 20) -> list[AuditLog]:
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
