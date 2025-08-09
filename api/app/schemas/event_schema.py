from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    club_id: int
    type: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    created_by: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    id: int

    class Config:
        orm_mode = True
