from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.workflow import WorkflowRun
from app.models.automation import Workflow, AutomationTask
from app.schemas.workflow import WorkflowOut, WorkflowRequest, WorkflowDefCreate, WorkflowDefOut
from app.services.workflows import apply_workflow_result, run_automation

router = APIRouter()

@router.post("/trigger/{workflow_id}")
async def trigger_workflow(
    workflow_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if not user.workspace_id:
        raise HTTPException(status_code=400, detail="User not in workspace")
    
    wf = await db.get(Workflow, workflow_id)
    if not wf or wf.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    task = AutomationTask(
        workspace_id=user.workspace_id,
        workflow_id=workflow_id,
        trigger_source="api",
        payload=payload,
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"message": "Workflow triggered", "task_id": task.id}

@router.get("/definitions", response_model=List[WorkflowDefOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> List[WorkflowDefOut]:
    if not user.workspace_id:
        return []
    result = await db.execute(select(Workflow).where(Workflow.workspace_id == user.workspace_id))
    return result.scalars().all()

@router.post("/definitions", response_model=WorkflowDefOut)
async def create_workflow(
    payload: WorkflowDefCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> WorkflowDefOut:
    if not user.workspace_id:
        raise HTTPException(status_code=400, detail="User not in workspace")
    new_wf = Workflow(
        workspace_id=user.workspace_id,
        name=payload.name,
        description=payload.description,
        trigger_type=payload.trigger_type,
        trigger_config=payload.trigger_config,
        nodes=payload.nodes
    )
    db.add(new_wf)
    await db.commit()
    await db.refresh(new_wf)
    return new_wf

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
async def list_workflow_runs(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WorkflowOut]:
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.user_id == user.id))
    return list(result.scalars().all())
