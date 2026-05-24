from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.workflow import WorkflowRun
from app.schemas.workflow import WorkflowOut, WorkflowRequest
from app.services.workflows import apply_workflow_result, run_automation
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

async def execute_workflow_task(run_id: int, workflow_type: str, payload: dict, user_id: int):
    """Background task to execute the workflow and update the database."""
    try:
        # We need a new session since we're in a background task
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                logger.error(f"WorkflowRun {run_id} not found in background task.")
                return

            # Simulate processing time for queue-style execution feel
            await asyncio.sleep(1)

            # run_automation is synchronous, we run it in a threadpool to not block the event loop
            output, status_text = await asyncio.to_thread(run_automation, workflow_type, payload)

            apply_workflow_result(run, output, status_text)

            db.add(AuditLog(user_id=user_id, event_type="workflow_run", detail=workflow_type))
            if status_text == "failed":
                db.add(AuditLog(user_id=user_id, event_type="workflow_failed", detail=output))

            await db.commit()
            logger.info(f"Background workflow {run_id} completed with status: {status_text}")
    except Exception as e:
        logger.error(f"Error executing background workflow {run_id}: {e}")

@router.post("/run", response_model=WorkflowOut)
async def run_workflow(
    payload: WorkflowRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> WorkflowOut:
    if not payload.workflow_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="workflow_type required")

    run = WorkflowRun(
        user_id=user.id,
        workflow_type=payload.workflow_type,
        input_summary=str(payload.payload)[:500],
        status="pending" # Indicate it's queued
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Queue the execution in the background
    background_tasks.add_task(execute_workflow_task, run.id, payload.workflow_type, payload.payload, user.id)

    return run


@router.get("/", response_model=list[WorkflowOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[WorkflowOut]:
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.user_id == user.id))
    return list(result.scalars().all())
