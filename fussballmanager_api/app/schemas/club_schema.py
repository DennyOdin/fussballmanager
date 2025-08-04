from pydantic import BaseModel
from typing import Optional

class ClubBase(BaseModel):
    name: str
    address: str
    founded_year: Optional[int] = None

class ClubCreate(ClubBase):
    pass

class ClubRead(ClubBase):
    id: int

    class Config:
        orm_mode = True
