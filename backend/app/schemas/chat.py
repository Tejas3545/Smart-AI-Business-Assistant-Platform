from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatSource(BaseModel):
    document_id: int
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: int
    assistant_message: str
    sources: List[ChatSource] = []
    lead_hint: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    role: str
    content: str

    class Config:
        orm_mode = True


class ConversationOut(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
