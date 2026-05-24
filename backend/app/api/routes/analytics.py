from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.analytics import AnalyticsSummary, AuditLogOut
from app.services.analytics import get_recent_audit_logs, get_summary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> AnalyticsSummary:
    data = await get_summary(db, user)
    return AnalyticsSummary(**data)


@router.get("/audit", response_model=list[AuditLogOut])
async def audit_logs(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[AuditLogOut]:
    logs = await get_recent_audit_logs(db, user)
    return logs
