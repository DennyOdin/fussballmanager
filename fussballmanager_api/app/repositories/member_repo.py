from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from uuid import UUID
from app.models.member_model import Member
from app.schemas.member_schema import MemberCreate, MemberUpdate, MemberFilter


class MemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_by_email(self, email: str) -> Optional[Member]:
        """Get member by email (case-insensitive)"""
        return self.db.query(Member).filter(
            func.lower(Member.email) == func.lower(email)
        ).first()

    def list_members(self, filters: MemberFilter) -> Tuple[List[Member], int]:
        """List members with filters and pagination"""
        query = self.db.query(Member)

        # Apply filters
        if filters.role:
            query = query.filter(Member.roles.contains([filters.role]))

        if filters.team is not None:
            query = query.filter(Member.team == filters.team)

        if filters.status:
            query = query.filter(Member.status == filters.status)

        if filters.q:
            search_term = f"%{filters.q}%"
            query = query.filter(
                or_(
                    func.lower(Member.first_name).like(func.lower(search_term)),
                    func.lower(Member.last_name).like(func.lower(search_term)),
                    func.lower(Member.email).like(func.lower(search_term)),
                    func.lower(
                        func.concat(Member.first_name, ' ', Member.last_name)
                    ).like(func.lower(search_term))
                )
            )

        # Order by creation date (newest first)
        query = query.order_by(Member.created_at.desc())

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        query = query.offset(filters.offset).limit(filters.limit)

        return query.all(), total

    def create_member(self, member_data: MemberCreate, created_by: Optional[str] = None) -> Member:
        """Create a new member"""
        member = Member(
            first_name=member_data.first_name,
            last_name=member_data.last_name,
            email=member_data.email,
            birthdate=member_data.birthdate,
            roles=member_data.roles,
            team=member_data.team,
            status=member_data.status,
            notes=member_data.notes,
            created_by=created_by
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update_member(
        self, 
        member_id: str, 
        member_data: MemberUpdate, 
        updated_by: Optional[str] = None
    ) -> Optional[Member]:
        """Update an existing member"""
        member = self.get_by_id(member_id)
        if not member:
            return None

        # Update only provided fields
        update_data = member_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        member.updated_by = updated_by
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete_member(self, member_id: str, updated_by: Optional[str] = None) -> bool:
        """Soft delete a member (set status to inactive)"""
        member = self.get_by_id(member_id)
        if not member:
            return False

        member.status = "inactive"
        member.updated_by = updated_by
        self.db.commit()
        return True

    def hard_delete_member(self, member_id: str) -> bool:
        """Hard delete a member from database"""
        member = self.get_by_id(member_id)
        if not member:
            return False

        self.db.delete(member)
        self.db.commit()
        return True

    def get_members_by_team(self, team: int, status: Optional[str] = None) -> List[Member]:
        """Get all members of a specific team"""
        query = self.db.query(Member).filter(Member.team == team)
        if status:
            query = query.filter(Member.status == status)
        return query.all()

    def get_members_by_role(self, role: str) -> List[Member]:
        """Get all members with a specific role"""
        return self.db.query(Member).filter(Member.roles.contains([role])).all()

    def check_email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Check if email already exists (case-insensitive)"""
        query = self.db.query(Member).filter(
            func.lower(Member.email) == func.lower(email)
        )
        if exclude_id:
            query = query.filter(Member.id != exclude_id)
        return query.first() is not None
