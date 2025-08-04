from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")  # or Enum
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)

    member = relationship("Member", backref="payments")
