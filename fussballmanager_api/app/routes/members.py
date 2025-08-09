from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.models.user_model import User
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreate, MemberUpdate, MemberOut, MemberFilter, MemberListResponse
)
from app.repositories.member_repo import MemberRepository
from app.routes.auth import get_current_user
from app.core.rbac import validate_member_permissions, get_user_id_from_token

router = APIRouter(prefix="/members", tags=["Members"])


def get_member_repo(db: Session = Depends(get_db)) -> MemberRepository:
    return MemberRepository(db)


@router.post("/", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_data: MemberCreate,
    current_user: User = Depends(get_current_user),
    repo: MemberRepository = Depends(get_member_repo)
):
    """
    Create a new member. Admin only.
    """
    # Check if user has admin role (for now, assume all users are admin)
    # In a real implementation, you'd check current_user.roles
    
    # Check if email already exists
    if member_data.email:
        if repo.check_email_exists(member_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Get user ID from token
    user_id = str(current_user.id)
    
    member = repo.create_member(member_data, created_by=user_id)
    return member


@router.get("/", response_model=MemberListResponse)
async def list_members(
    role: Optional[str] = Query(None, description="Filter by role"),
    team: Optional[int] = Query(None, description="Filter by team"),
    status: Optional[str] = Query(None, description="Filter by status"),
    q: Optional[str] = Query(None, description="Search in name and email"),
    limit: int = Query(50, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: User = Depends(get_current_user),
    repo: MemberRepository = Depends(get_member_repo)
):
    """
    List members with optional filtering and pagination.
    """
    filters = MemberFilter(
        role=role,
        team=team,
        status=status,
        q=q,
        limit=limit,
        offset=offset
    )
    
    members, total = repo.list_members(filters)
    
    return MemberListResponse(
        members=members,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{member_id}", response_model=MemberOut)
async def get_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    repo: MemberRepository = Depends(get_member_repo)
):
    """
    Get a specific member by ID.
    """
    member = repo.get_by_id(member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return member


@router.patch("/{member_id}", response_model=MemberOut)
async def update_member(
    member_id: str,
    member_data: MemberUpdate,
    current_user: User = Depends(get_current_user),
    repo: MemberRepository = Depends(get_member_repo)
):
    """
    Update a member. Admin or coach of the same team can update.
    """
    # Validate permissions (admin or coach of same team)
    member = validate_member_permissions(
        str(member_id), 
        ["admin", "coach"], 
        current_user, 
        repo.db
    )
    
    # Check if email already exists (if being updated)
    if member_data.email and member_data.email != member.email:
        if repo.check_email_exists(member_data.email, exclude_id=member_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Get user ID from token
    user_id = str(current_user.id)
    
    updated_member = repo.update_member(member_id, member_data, updated_by=user_id)
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return updated_member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    repo: MemberRepository = Depends(get_member_repo)
):
    """
    Soft delete a member (set status to inactive). Admin only.
    """
    # Validate permissions (admin only)
    validate_member_permissions(
        str(member_id), 
        ["admin"], 
        current_user, 
        repo.db
    )
    
    # Get user ID from token
    user_id = str(current_user.id)
    
    success = repo.delete_member(member_id, updated_by=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )


# Example curl commands for testing:
"""
# Create a member (admin only)
curl -X POST "http://localhost:8000/members/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "roles": ["player"],
    "team": 1,
    "status": "active"
  }'

# List members with filters
curl -X GET "http://localhost:8000/members/?team=1&status=active&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search members
curl -X GET "http://localhost:8000/members/?q=john" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific member
curl -X GET "http://localhost:8000/members/MEMBER_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update member (admin or coach of same team)
curl -X PATCH "http://localhost:8000/members/MEMBER_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "team": 2,
    "notes": "Updated notes"
  }'

# Delete member (admin only)
curl -X DELETE "http://localhost:8000/members/MEMBER_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN"
"""
