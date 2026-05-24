import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import AsyncSessionLocal as SessionLocal, engine
from app.models.user import User
from app.models.workspace import Workspace
from app.models.automation import Workflow, AutomationTask
from app.models.integration import Integration
from app.services.automation import process_task
from app.db.base import Base

async def test_engine():
    # Make sure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as db:
        import uuid
        test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        # Create a user
        user = User(email=test_email, full_name="tester", hashed_password="hash")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create a workspace
        workspace = Workspace(name="Test Workspace", owner_id=user.id)
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)
        
        # Create an integration
        integration = Integration(
            workspace_id=workspace.id,
            provider="webhook",
            status="active",
            credentials={}
        )
        db.add(integration)
        
        # Create a workflow
        nodes = [
            {"type": "condition", "field": "lead_score", "operator": ">", "value": 50},
            {"type": "action", "provider": "webhook", "config": {"url": "https://httpbin.org/post", "method": "POST"}}
        ]
        
        workflow = Workflow(
            workspace_id=workspace.id,
            name="High Score Lead Webhook",
            trigger_type="lead_created",
            nodes=nodes
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        # Create an automation task
        task = AutomationTask(
            workspace_id=workspace.id,
            workflow_id=workflow.id,
            payload={"lead_score": 75, "email": "test@example.com"},
            status="pending"
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        print(f"Created Task ID: {task.id} with initial status: {task.status}")
        
        # Process task step 1 (Condition)
        print("Processing task (Node 1: Condition Check)...")
        await process_task(task.id)
        
        # Re-fetch from db
        await db.refresh(task)
        print(f"Task status after node 1: {task.status}, step_index: {task.step_index}")
        
        # Process task step 2 (Action)
        if task.status == "pending":
            print("Processing task (Node 2: Webhook Action)...")
            await process_task(task.id)
            
            await db.refresh(task)
            print(f"Task status after node 2: {task.status}, step_index: {task.step_index}")
            
        print(f"Final Error Log: {task.error_log}")
        
        # Clean up mock test data
        await db.delete(task)
        await db.delete(workflow)
        await db.delete(integration)
        await db.delete(workspace)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(test_engine())
