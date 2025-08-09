from pydantic import BaseModel
from typing import Optional
from datetime import date

class PaymentBase(BaseModel):
    member_id: int
    amount: float
    due_date: date
    status: Optional[str] = "unpaid"
    payment_date: Optional[date] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: int

    class Config:
        orm_mode = True
