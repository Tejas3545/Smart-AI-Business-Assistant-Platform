import asyncio
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.models.automation import AutomationTask, Workflow
from app.models.integration import Integration
from app.services.integrations import execute_webhook, send_slack_message, send_email_smtp, sync_crm_dummy, sync_crm_hubspot
import traceback

logger = logging.getLogger(__name__)

async def process_task(db: AsyncSession, task: AutomationTask):
    try:
        # Get the workflow
        workflow = await db.get(Workflow, task.workflow_id)
        if not workflow or not workflow.nodes:
            task.status = "failed"
            task.error_log = "Workflow or nodes not found"
            return
            
        nodes = workflow.nodes
        if not isinstance(nodes, list):
            task.status = "failed"
            task.error_log = "Workflow nodes must be a list"
            return
            
        current_node_idx = task.step_index
        if current_node_idx >= len(nodes):
            task.status = "completed"
            return
            
        node = nodes[current_node_idx]
        node_type = node.get("type")
        
        # Execute the node based on type
        if node_type == "condition":
            # Simple condition logic
            condition_field = node.get("field")
            condition_value = node.get("value")
            operator = node.get("operator", "==")
            
            payload_val = task.payload.get(condition_field)
            passed = False
            if operator == "==":
                passed = (payload_val == condition_value)
            elif operator == ">":
                try:
                    passed = (float(payload_val) > float(condition_value))
                except:
                    pass
                    
            if passed:
                task.step_index += 1
            else:
                task.status = "completed" # Workflow ends here if condition fails
                task.error_log = "Condition failed"
                return
                
        elif node_type in ("action", "follow_up"):
            provider = node.get("provider")
            action_config = node.get("config", {})
            
            # Fetch integration credentials if needed
            integration = None
            if provider:
                result = await db.execute(select(Integration).where(
                    Integration.workspace_id == task.workspace_id,
                    Integration.provider == provider,
                    Integration.status == "active"
                ))
                integration = result.scalars().first()
                
            creds = integration.credentials if integration else {}
            
            if provider == "webhook":
                await execute_webhook(
                    url=action_config.get("url"),
                    method=action_config.get("method", "POST"),
                    headers=action_config.get("headers", {}),
                    payload=task.payload
                )
            elif provider == "slack":
                webhook_url = creds.get("webhook_url") or action_config.get("webhook_url")
                message = action_config.get("message", str(task.payload))
                if webhook_url:
                    await send_slack_message(webhook_url, message)
            elif provider == "gmail":
                smtp_host = creds.get("smtp_host", "smtp.gmail.com")
                smtp_port = creds.get("smtp_port", 587)
                username = creds.get("username")
                password = creds.get("password")
                to_email = action_config.get("to_email")
                subject = action_config.get("subject", "Automation Notification")
                body = action_config.get("body", str(task.payload))
                
                if username and password and to_email:
                    # Run synchronous function in executor if needed, but for simplicity we'll just run it
                    # Ideally use aiosmtplib, but standard smtplib is blocking.
                    import concurrent.futures
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        await loop.run_in_executor(pool, send_email_smtp, smtp_host, smtp_port, username, password, to_email, subject, body)
            elif provider == "crm_hubspot":
                api_key = creds.get("api_key")
                await sync_crm_hubspot(api_key, task.payload)
            elif provider == "crm":
                api_key = creds.get("api_key")
                await sync_crm_dummy(api_key, task.payload)
                
            task.step_index += 1
            
        else:
            task.step_index += 1 # Unknown node, skip
            
        # If we reached the end
        if task.step_index >= len(nodes):
            task.status = "completed"
        else:
            task.status = "pending" # Needs to process next node
            task.next_run_at = datetime.now(timezone.utc)
            
    except Exception as e:
        task.retry_count += 1
        task.error_log = traceback.format_exc()
        if task.retry_count >= task.max_retries:
            task.status = "failed"
        else:
            task.status = "retrying"
            task.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=2 ** task.retry_count)

async def run_worker():
    logger.info("Starting automation background worker...")
    while True:
        try:
            async with SessionLocal() as db:
                # Find pending or retrying tasks
                result = await db.execute(
                    select(AutomationTask).where(
                        AutomationTask.status.in_(["pending", "retrying"]),
                        AutomationTask.next_run_at <= func.now()
                    ).order_by(AutomationTask.next_run_at.asc()).limit(10)
                )
                tasks = result.scalars().all()
                
                for task in tasks:
                    task.status = "processing"
                    await db.commit()
                    
                    await process_task(db, task)
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Worker error: {e}")
            
        await asyncio.sleep(5)
