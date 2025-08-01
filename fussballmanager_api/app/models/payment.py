from pydantic import BaseModel
from typing import Optional

class Payment(BaseModel):
    id: int
    member_id: int
    amount: float
    due_date: str
    status: str
    payment_date: Optional[str] = None
