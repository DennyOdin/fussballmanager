from pydantic import BaseModel
from typing import Optional
from datetime import date

class MemberBase(BaseModel):
    user_id: int
    team: Optional[str] = None
    status: Optional[str] = "active"
    join_date: Optional[date] = None
    leave_date: Optional[date] = None

class MemberCreate(MemberBase):
    pass

class MemberRead(MemberBase):
    id: int

    class Config:
        orm_mode = True
