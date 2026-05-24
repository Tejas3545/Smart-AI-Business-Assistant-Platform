from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class WorkflowRequest(BaseModel):
    workflow_type: str
    payload: dict

class WorkflowOut(BaseModel):
    id: int
    workflow_type: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None

    model_config = {"from_attributes": True}

class WorkflowDefCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)

class WorkflowDefOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    is_active: bool

    model_config = {"from_attributes": True}
