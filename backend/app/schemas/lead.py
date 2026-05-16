from typing import Optional

from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    interest: Optional[str] = None
    notes: Optional[str] = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    interest: Optional[str] = None
    score: int
    status: str

    class Config:
        orm_mode = True


class LeadFollowUp(BaseModel):
    lead_id: int
    message: str
