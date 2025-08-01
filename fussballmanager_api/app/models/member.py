from pydantic import BaseModel
from typing import Optional

class Member(BaseModel):
    id: int
    club_id: int
    name: str
    birthdate: str
    role: str
    team: Optional[str] = None
    joined_date: Optional[str] = None
    is_active: bool = True
