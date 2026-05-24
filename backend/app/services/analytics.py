from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.document import Document
from app.models.lead import Lead
from app.models.message import Message
from app.models.workflow import WorkflowRun
from app.models.audit import AuditLog
from app.models.automation import AutomationTask
from app.models.user import User


async def get_summary(db: AsyncSession, user: User) -> dict:
    user_ids_query = select(User.id)
    if user.workspace_id:
        user_ids_query = user_ids_query.where(User.workspace_id == user.workspace_id)
    else:
        user_ids_query = user_ids_query.where(User.id == user.id)
    user_ids_subquery = user_ids_query.subquery()

    total_conversations = await db.scalar(
        select(func.count(Conversation.id)).where(Conversation.user_id.in_(select(user_ids_subquery.c.id)))
    )
    total_messages = await db.scalar(
        select(func.count(Message.id)).join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id.in_(select(user_ids_subquery.c.id)))
    )
    total_leads = await db.scalar(
        select(func.count(Lead.id)).where(Lead.user_id.in_(select(user_ids_subquery.c.id)))
    )
    hot_leads = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.user_id.in_(select(user_ids_subquery.c.id)), Lead.status == "hot"
        )
    )
    warm_leads = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.user_id.in_(select(user_ids_subquery.c.id)), Lead.status == "warm"
        )
    )
    cold_leads = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.user_id.in_(select(user_ids_subquery.c.id)), Lead.status == "cold"
        )
    )
    workflow_runs = await db.scalar(
        select(func.count(WorkflowRun.id)).where(WorkflowRun.user_id.in_(select(user_ids_subquery.c.id)))
    )
    documents_uploaded = await db.scalar(
        select(func.count(Document.id)).where(Document.user_id.in_(select(user_ids_subquery.c.id)))
    )
    workflow_failures_query = select(func.count(AutomationTask.id)).where(AutomationTask.status == "failed")
    if user.workspace_id:
        workflow_failures_query = workflow_failures_query.where(AutomationTask.workspace_id == user.workspace_id)
    else:
        workflow_failures_query = workflow_failures_query.where(AutomationTask.workspace_id == -1)
    workflow_failures = await db.scalar(workflow_failures_query)
    
    total_user_tokens = await db.scalar(
        select(func.coalesce(func.sum(Message.tokens), 0))
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id.in_(select(user_ids_subquery.c.id)), Message.role == "user")
    )
    total_ai_tokens = await db.scalar(
        select(func.coalesce(func.sum(Message.tokens), 0))
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id.in_(select(user_ids_subquery.c.id)), Message.role == "assistant")
    )

    message_result = await db.execute(
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id.in_(select(user_ids_subquery.c.id)))
        .order_by(Message.conversation_id.asc(), Message.created_at.asc())
    )
    messages = message_result.scalars().all()
    response_time_total = 0.0
    response_time_count = 0
    last_user_time_by_conversation: dict[int, datetime] = {}
    for message in messages:
        if message.role == "user":
            last_user_time_by_conversation[message.conversation_id] = message.created_at
        elif message.role == "assistant":
            last_user_time = last_user_time_by_conversation.pop(message.conversation_id, None)
            if last_user_time:
                delta = (message.created_at - last_user_time).total_seconds()
                if delta >= 0:
                    response_time_total += delta
                    response_time_count += 1

    avg_response_seconds = round(response_time_total / response_time_count, 2) if response_time_count else 0.0
    conversion_rate = round((hot_leads or 0) / (total_leads or 1) * 100, 2) if total_leads else 0.0

    return {
        "total_conversations": total_conversations or 0,
        "total_messages": total_messages or 0,
        "total_leads": total_leads or 0,
        "hot_leads": hot_leads or 0,
        "warm_leads": warm_leads or 0,
        "cold_leads": cold_leads or 0,
        "workflow_runs": workflow_runs or 0,
        "documents_uploaded": documents_uploaded or 0,
        "workflow_failures": workflow_failures or 0,
        "conversion_rate": conversion_rate,
        "avg_response_seconds": avg_response_seconds,
        "total_user_tokens": total_user_tokens or 0,
        "total_ai_tokens": total_ai_tokens or 0,
    }


async def get_recent_audit_logs(db: AsyncSession, user: User, limit: int = 20) -> list[AuditLog]:
    user_ids_query = select(User.id)
    if user.workspace_id:
        user_ids_query = user_ids_query.where(User.workspace_id == user.workspace_id)
    else:
        user_ids_query = user_ids_query.where(User.id == user.id)
    user_ids_subquery = user_ids_query.subquery()

    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.user_id.in_(select(user_ids_subquery.c.id)))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
