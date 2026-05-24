from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import engine
from app.models.user import User
from app.models.automation import AutomationTask
from app.models.workspace import Workspace
from app.models.integration import Integration
from app.models.audit import AuditLog
from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.get("/users")
async def list_clients(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(User))
    return result.scalars().all()

@router.get("/workspaces")
async def list_workspaces(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(Workspace))
    return result.scalars().all()

@router.get("/automation-logs")
async def get_automation_logs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(AutomationTask).order_by(AutomationTask.created_at.desc()).limit(100))
    return result.scalars().all()

@router.get("/integrations")
async def list_integrations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(Integration).order_by(Integration.created_at.desc()))
    return result.scalars().all()

@router.get("/audit-logs")
async def list_audit_logs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200))
    return result.scalars().all()
