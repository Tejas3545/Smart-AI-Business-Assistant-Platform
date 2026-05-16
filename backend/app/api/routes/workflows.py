from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.workflow import WorkflowRun
from app.schemas.workflow import WorkflowOut, WorkflowRequest
from app.services.workflows import apply_workflow_result, run_automation

router = APIRouter()


@router.post("/run", response_model=WorkflowOut)
async def run_workflow(
    payload: WorkflowRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> WorkflowOut:
    if not payload.workflow_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="workflow_type required")

    run = WorkflowRun(
        user_id=user.id,
        workflow_type=payload.workflow_type,
        input_summary=str(payload.payload)[:500],
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    output, status_text = run_automation(payload.workflow_type, payload.payload)
    apply_workflow_result(run, output, status_text)
    await db.commit()
    await db.refresh(run)

    db.add(AuditLog(user_id=user.id, event_type="workflow_run", detail=payload.workflow_type))
    if status_text == "failed":
        db.add(AuditLog(user_id=user.id, event_type="workflow_failed", detail=output))
    await db.commit()

    return run


@router.get("/", response_model=list[WorkflowOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WorkflowOut]:
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.user_id == user.id))
    return list(result.scalars().all())
