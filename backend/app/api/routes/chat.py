from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource, ConversationOut, MessageOut
from app.services.agents import execute_plan, plan_intent, validate_response
from app.services.memory import add_message, ensure_conversation
from app.services.rag import get_rag_store

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ChatResponse:
    conversation = await ensure_conversation(db, user.id, payload.conversation_id)
    if not conversation.title or conversation.title == "New Conversation":
        words = payload.message.strip().split()
        if words:
            conversation.title = " ".join(words[:6])[:255]
    await add_message(db, conversation.id, "user", payload.message)

    rag = get_rag_store()
    raw_sources = rag.query(user.id, payload.message)
    # Convert raw dicts to typed ChatSource objects for proper serialization
    sources = [
        ChatSource(document_id=s["document_id"], snippet=s["snippet"])
        for s in raw_sources
        if "document_id" in s and "snippet" in s
    ]

    intent = plan_intent(payload.message)
    result = execute_plan(intent, payload.message, raw_sources)
    reply = validate_response(result["reply"], raw_sources)

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
    result = await db.execute(
        select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[MessageOut]:
    owns_conversation = await db.execute(
        select(Conversation.id).where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    if not owns_conversation.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id == user.id, Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    message_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    for msg in message_result.scalars().all():
        await db.delete(msg)
    await db.delete(conversation)
    db.add(AuditLog(user_id=user.id, event_type="chat_deleted", detail=f"conversation_id={conversation_id}"))
    await db.commit()


@router.delete("/conversations", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_conversations(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    convo_result = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
    conversations = convo_result.scalars().all()
    for conversation in conversations:
        message_result = await db.execute(
            select(Message).where(Message.conversation_id == conversation.id)
        )
        for msg in message_result.scalars().all():
            await db.delete(msg)
        await db.delete(conversation)

    db.add(AuditLog(user_id=user.id, event_type="chat_deleted_all", detail=f"count={len(conversations)}"))
    await db.commit()
