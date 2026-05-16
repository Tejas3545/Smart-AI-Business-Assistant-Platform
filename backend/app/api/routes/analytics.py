from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ensure_admin, get_db
from app.schemas.analytics import AnalyticsSummary, AuditLogOut
from app.services.analytics import get_recent_audit_logs, get_summary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(ensure_admin),
) -> AnalyticsSummary:
    data = await get_summary(db)
    return AnalyticsSummary(**data)


@router.get("/audit", response_model=list[AuditLogOut])
async def audit_logs(
    db: AsyncSession = Depends(get_db),
    user=Depends(ensure_admin),
) -> list[AuditLogOut]:
    logs = await get_recent_audit_logs(db)
    return logs
