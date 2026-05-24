from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.models.workspace import Workspace


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, full_name: str, password: str) -> User:
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
    db.add(user)
    await db.flush()

    workspace = Workspace(
        name=f"{full_name}'s Workspace",
        owner_id=user.id,
        settings={},
    )
    db.add(workspace)
    await db.flush()

    user.workspace_id = workspace.id
    await db.commit()
    await db.refresh(user)
    return user
