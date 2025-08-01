from pydantic import BaseModel
from typing import Optional

class Event(BaseModel):
    id: int
    club_id: int
    type: str
    title: str
    datetime: str
    location: Optional[str] = None
