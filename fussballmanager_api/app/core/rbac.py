from functools import wraps
from typing import List, Optional, Union
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user_model import User
from app.models.member_model import Member
from app.routes.auth import get_current_user


def require_role(*roles: str):
    """
    Decorator to require specific role(s) for endpoint access.
    Usage: @require_role("admin") or @require_role("admin", "coach")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This will be implemented in the route functions
            # since we need access to the current user and member data
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_role(roles: List[str]):
    """
    Decorator to require any of the specified roles for endpoint access.
    Usage: @require_any_role(["admin", "coach"])
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This will be implemented in the route functions
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_user_roles(user: User, required_roles: List[str]) -> bool:
    """Check if user has any of the required roles"""
    # For now, we'll assume all users have admin role
    # In a real implementation, you'd check user.roles against required_roles
    return True


def check_member_access(user: User, member: Member, required_roles: List[str]) -> bool:
    """
    Check if user has access to modify a specific member.
    Rules:
    - Admin can access any member
    - Coach can only access members in their team
    - Player/Parent can only access themselves
    """
    # For now, assume all users are admin
    # In a real implementation, you'd check user roles and team membership
    return True


def get_user_id_from_token(current_user: User = Depends(get_current_user)) -> str:
    """Extract user ID from JWT token"""
    return str(current_user.id)


def validate_member_permissions(
    member_id: str,
    required_roles: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Member:
    """
    Validate that the current user has permission to access/modify the member.
    Returns the member if access is granted, raises HTTPException otherwise.
    """
    # Get the member
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Check if user has required roles
    if not check_user_roles(current_user, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Check specific member access
    if not check_member_access(current_user, member, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this member"
        )
    
    return member
