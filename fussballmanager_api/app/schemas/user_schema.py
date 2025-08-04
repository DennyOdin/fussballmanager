from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    coach = "coach"
    player = "player"
    parent = "parent"

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole
    club_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True
