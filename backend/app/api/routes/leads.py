from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadFollowUp, LeadOut
from app.services.leads import update_lead_with_score
from app.services.user_memory import upsert_memory

router = APIRouter()


@router.post("/", response_model=LeadOut)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> LeadOut:
    lead = Lead(
        user_id=user.id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        interest=payload.interest,
        notes=payload.notes,
    )
    lead = update_lead_with_score(lead)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    db.add(AuditLog(user_id=user.id, event_type="lead_created", detail=lead.name))
    await db.commit()

    await upsert_memory(db, user.id, "last_lead", f"{lead.name} ({lead.status})")

    return lead


@router.get("/", response_model=list[LeadOut])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[LeadOut]:
    result = await db.execute(select(Lead).where(Lead.user_id == user.id))
    return list(result.scalars().all())


@router.get("/{lead_id}/followup", response_model=LeadFollowUp)
async def followup_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> LeadFollowUp:
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    message = (
        f"Hi {lead.name}, thanks for your interest in our services. "
        "I would love to understand your needs and share the next steps. "
        "Would you like to schedule a quick call this week?"
    )

    return LeadFollowUp(lead_id=lead.id, message=message)
