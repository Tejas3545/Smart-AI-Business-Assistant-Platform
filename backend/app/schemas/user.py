from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    class Config:
        orm_mode = True
