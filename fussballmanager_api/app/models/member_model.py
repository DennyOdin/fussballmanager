from sqlalchemy import Column, String, Date, Integer, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional
import uuid
from app.db.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    birthdate = Column(Date, nullable=True)
    roles = Column(JSON, nullable=False, default=list)
    team = Column(Integer, nullable=True, index=True)
    status = Column(String(20), nullable=False, default="active")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_members_team_status', 'team', 'status'),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
