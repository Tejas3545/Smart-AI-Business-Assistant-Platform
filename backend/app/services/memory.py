from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message


async def ensure_conversation(db: AsyncSession, user_id: int, conversation_id: int | None) -> Conversation:
    if conversation_id:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        convo = result.scalar_one_or_none()
        if convo:
            return convo

    convo = Conversation(user_id=user_id)
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


async def add_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    tokens: int = 0,
) -> Message:
    if tokens == 0:
        tokens = max(1, len(content.split()))
    message = Message(conversation_id=conversation_id, role=role, content=content, tokens=tokens)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_recent_messages(db: AsyncSession, conversation_id: int, limit: int = 6) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))
