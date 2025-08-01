from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool = True
    role: str
