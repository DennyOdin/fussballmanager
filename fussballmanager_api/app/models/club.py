from pydantic import BaseModel
from typing import Optional

class club(BaseModel):
    id: int
    name: str
    address: str
    founded_year: Optional[int] = None
    admin_user_ids: list[int] = []
