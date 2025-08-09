from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal
from datetime import date, datetime


class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    birthdate: Optional[date] = None
    roles: List[str] = Field(default_factory=list)
    team: Optional[int] = None
    status: Literal["active", "inactive"] = "active"
    notes: Optional[str] = None

    @validator('roles')
    def validate_roles(cls, v):
        allowed_roles = {"admin", "coach", "player", "parent"}
        for role in v:
            if role not in allowed_roles:
                raise ValueError(f"Invalid role: {role}. Allowed roles: {allowed_roles}")
        return v


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    birthdate: Optional[date] = None
    roles: Optional[List[str]] = None
    team: Optional[int] = None
    status: Optional[Literal["active", "inactive"]] = None
    notes: Optional[str] = None

    @validator('roles')
    def validate_roles(cls, v):
        if v is not None:
            allowed_roles = {"admin", "coach", "player", "parent"}
            for role in v:
                if role not in allowed_roles:
                    raise ValueError(f"Invalid role: {role}. Allowed roles: {allowed_roles}")
        return v


class MemberOut(MemberBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class MemberFilter(BaseModel):
    role: Optional[str] = None
    team: Optional[int] = None
    status: Optional[Literal["active", "inactive"]] = None
    q: Optional[str] = None  # Search query for name/email
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = {"admin", "coach", "player", "parent"}
            if v not in allowed_roles:
                raise ValueError(f"Invalid role: {v}. Allowed roles: {allowed_roles}")
        return v


class MemberListResponse(BaseModel):
    members: List[MemberOut]
    total: int
    limit: int
    offset: int
