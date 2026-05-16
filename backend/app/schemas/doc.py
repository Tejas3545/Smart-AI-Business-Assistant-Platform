from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str | None = None
    source: str | None = None

    model_config = {"from_attributes": True}
