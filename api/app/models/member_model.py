from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team = Column(String, nullable=True)
    status = Column(String, default="active")
    join_date = Column(Date, nullable=True)
    leave_date = Column(Date, nullable=True)

    user = relationship("User", backref="member")
