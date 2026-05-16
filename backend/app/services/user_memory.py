from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_memory import UserMemory


async def upsert_memory(db: AsyncSession, user_id: int, key: str, value: str) -> UserMemory:
    result = await db.execute(
        select(UserMemory).where(UserMemory.user_id == user_id, UserMemory.key == key)
    )
    memory = result.scalar_one_or_none()
    if memory:
        memory.value = value
    else:
        memory = UserMemory(user_id=user_id, key=key, value=value)
        db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return memory


async def list_memory(db: AsyncSession, user_id: int) -> list[UserMemory]:
    result = await db.execute(select(UserMemory).where(UserMemory.user_id == user_id))
    return list(result.scalars().all())
