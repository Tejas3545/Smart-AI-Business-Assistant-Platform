from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, ConversationOut, MessageOut
from app.services.agents import execute_plan, plan_intent, validate_response
from app.services.memory import add_message, ensure_conversation
from app.services.rag import rag_store
from app.services.user_memory import list_memory

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ChatResponse:
    conversation = await ensure_conversation(db, user.id, payload.conversation_id)
    await add_message(db, conversation.id, "user", payload.message)

    sources = rag_store.query(user.id, payload.message)
    intent = plan_intent(payload.message)
    result = execute_plan(intent, payload.message, sources)
    reply = validate_response(result["reply"], sources)

    memories = await list_memory(db, user.id)
    if memories:
        memory_lines = "; ".join(f"{item.key}: {item.value}" for item in memories[:3])
        reply = f"{reply}\n\nSaved memory: {memory_lines}"

    await add_message(db, conversation.id, "assistant", reply)

    db.add(AuditLog(user_id=user.id, event_type="chat", detail=f"intent={intent}"))
    await db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        assistant_message=reply,
        sources=sources,
        lead_hint=result.get("lead_hint"),
    )


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[ConversationOut]:
    result = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
    return list(result.scalars().all())


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[MessageOut]:
    result = await db.execute(
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id == user.id, Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())
