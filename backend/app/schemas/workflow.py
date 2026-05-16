from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    workflow_type: str
    payload: dict


class WorkflowOut(BaseModel):
    id: int
    workflow_type: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None

    class Config:
        orm_mode = True
