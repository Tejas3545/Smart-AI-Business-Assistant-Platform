from datetime import datetime

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_conversations: int
    total_messages: int
    total_leads: int
    hot_leads: int
    workflow_runs: int
    documents_uploaded: int
    total_user_tokens: int
    total_ai_tokens: int


class AuditLogOut(BaseModel):
    id: int
    event_type: str
    detail: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
