from app.models.workflow import WorkflowRun
import httpx
import logging
from typing import Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

MOCK_WEBHOOK_URL = "https://httpbin.org/post"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True
)
def _mock_integration_call(service_name: str, payload: dict) -> Tuple[bool, str]:
    """Simulates calling a real external service API via POST with retry logic."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                MOCK_WEBHOOK_URL,
                json={"service": service_name, "data": payload}
            )
            response.raise_for_status()
            # In a real scenario we'd parse response.json()
            return True, f"Successfully integrated with {service_name}"
    except httpx.HTTPError as e:
        logger.error(f"Integration with {service_name} failed: {e}")
        raise # Reraise to trigger Tenacity retry

def run_automation(workflow_type: str, payload: dict) -> tuple[str, str]:
    try:
        if workflow_type == "email_summary":
            success, msg = _mock_integration_call("Gmail", payload)
            if success:
                output = f"Summary created for email subject: {payload.get('subject', 'N/A')}. {msg}"
                return output, "success"

        elif workflow_type == "crm_sync":
            success, msg = _mock_integration_call("Salesforce/HubSpot", payload)
            if success:
                output = f"CRM sync completed for {payload.get('record', 'lead')}. {msg}"
                return output, "success"

        elif workflow_type == "calendar_booking":
            success, msg = _mock_integration_call("Google Calendar", payload)
            if success:
                output = f"Calendar booking confirmed for {payload.get('date', 'next available slot')}. {msg}"
                return output, "success"

        elif workflow_type == "lead_enrichment":
            success, msg = _mock_integration_call("Clearbit/Apollo", payload)
            if success:
                output = f"Lead data enriched. {msg}"
                return output, "success"
        else:
            return "Unsupported workflow type", "failed"

    except httpx.HTTPError as e:
        logger.error(f"Workflow {workflow_type} failed after retries: {e}")
        return f"Integration failed after retries: {e}", "failed"
    except Exception as e:
        logger.error(f"Workflow {workflow_type} encountered unexpected error: {e}")
        return f"Unexpected error: {e}", "failed"

    return "Failed to complete workflow.", "failed"

def apply_workflow_result(run: WorkflowRun, output: str, status: str) -> WorkflowRun:
    run.output_summary = output
    run.status = status
    return run
