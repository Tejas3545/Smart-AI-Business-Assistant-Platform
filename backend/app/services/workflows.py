from app.models.workflow import WorkflowRun


def run_automation(workflow_type: str, payload: dict) -> tuple[str, str]:
    if workflow_type == "email_summary":
        output = f"Summary created for email subject: {payload.get('subject', 'N/A')}"
        return output, "success"
    if workflow_type == "crm_sync":
        output = f"CRM sync queued for {payload.get('record', 'lead')}"
        return output, "success"
    if workflow_type == "calendar_booking":
        output = f"Calendar booking proposed for {payload.get('date', 'next available slot')}"
        return output, "success"
    return "Unsupported workflow type", "failed"


def apply_workflow_result(run: WorkflowRun, output: str, status: str) -> WorkflowRun:
    run.output_summary = output
    run.status = status
    return run
