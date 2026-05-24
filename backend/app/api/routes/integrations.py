from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List

from app.db.session import engine
from app.models.integration import Integration
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

class IntegrationCreate(BaseModel):
    provider: str
    credentials: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)

class IntegrationOut(BaseModel):
    id: int
    provider: str
    status: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[IntegrationOut])
async def list_integrations(current_user: User = Depends(get_current_user)):
    if not current_user.workspace_id:
        return []
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Integration).where(Integration.workspace_id == current_user.workspace_id)
        )
        return result.scalars().all()

@router.post("/", response_model=IntegrationOut)
async def create_integration(integration: IntegrationCreate, current_user: User = Depends(get_current_user)):
    if not current_user.workspace_id:
        raise HTTPException(status_code=400, detail="User does not belong to a workspace")
        
    async with AsyncSession(engine) as session:
        new_int = Integration(
            workspace_id=current_user.workspace_id,
            provider=integration.provider,
            credentials=integration.credentials,
            config=integration.config,
            status="active"
        )
        session.add(new_int)
        await session.commit()
        await session.refresh(new_int)
        return new_int
