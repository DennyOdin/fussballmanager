import pytest
import sys
import os
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add the fussballmanager_api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db.database import get_db
from app.models.member_model import Member
from sqlalchemy.orm import Session
import uuid

# Test client
client = TestClient(app)


def get_test_db():
    """Get test database session"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_token():
    """Get authentication token for testing"""
    # Try to register a test user (might already exist)
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass"
    }
    response = client.post("/auth/register", json=register_data)
    # Don't assert status code - user might already exist
    
    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with authentication token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestMembersAPI:
    """Test Members API endpoints"""
    
    def test_create_member(self, auth_headers):
        """Test creating a new member"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{unique_id}@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "active",
            "notes": "Test member"
        }
        
        response = client.post("/members/", json=member_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == member_data["email"]  # Use the dynamic email
        assert data["roles"] == ["player"]
        assert data["team"] == 1
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert data["created_by"] is not None
        
        return data["id"]
    
    def test_get_member(self, auth_headers):
        """Test getting a specific member"""
        # First create a member
        member_id = self.test_create_member(auth_headers)
        
        # Then get it
        response = client.get(f"/members/{member_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == member_id
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
    
    def test_update_member(self, auth_headers):
        """Test updating a member"""
        # First create a member
        member_id = self.test_create_member(auth_headers)
        
        # Then update it
        update_data = {
            "team": 2,
            "notes": "Updated notes"
        }
        
        response = client.patch(f"/members/{member_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["team"] == 2
        assert data["notes"] == "Updated notes"
        assert data["updated_at"] is not None
        assert data["updated_by"] is not None
    
    def test_delete_member(self, auth_headers):
        """Test soft deleting a member"""
        # First create a member
        member_id = self.test_create_member(auth_headers)
        
        # Then delete it
        response = client.delete(f"/members/{member_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify it's soft deleted by getting it
        response = client.get(f"/members/{member_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "inactive"
    
    def test_list_members(self, auth_headers):
        """Test listing members with filters"""
        import uuid
        unique_id1 = str(uuid.uuid4())[:8]
        unique_id2 = str(uuid.uuid4())[:8]
        
        # Create a few members
        member1_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{unique_id1}@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "active"
        }
        
        member2_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": f"jane.smith.{unique_id2}@example.com",
            "roles": ["coach"],
            "team": 1,
            "status": "active"
        }
        
        client.post("/members/", json=member1_data, headers=auth_headers)
        client.post("/members/", json=member2_data, headers=auth_headers)
        
        # Test listing all members
        response = client.get("/members/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "members" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["members"]) >= 2
        
        # Test filtering by team
        response = client.get("/members/?team=1", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for member in data["members"]:
            assert member["team"] == 1
        
        # Test filtering by status
        response = client.get("/members/?status=active", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for member in data["members"]:
            assert member["status"] == "active"
    
    def test_search_members(self, auth_headers):
        """Test searching members"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Create a member
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{unique_id}@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "active"
        }
        
        client.post("/members/", json=member_data, headers=auth_headers)
        
        # Test search by name
        response = client.get("/members/?q=john", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["members"]) >= 1
        assert any("john" in member["first_name"].lower() for member in data["members"])
        
        # Test search by email
        response = client.get("/members/?q=john.doe@example.com", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["members"]) >= 1
        assert any("john.doe@example.com" in member["email"] for member in data["members"])
    
    def test_validation_errors(self, auth_headers):
        """Test validation errors"""
        # Test invalid roles
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "roles": ["invalid_role"],
            "team": 1,
            "status": "active"
        }
        
        response = client.post("/members/", json=member_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # Test invalid status
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "invalid_status"
        }
        
        response = client.post("/members/", json=member_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_duplicate_email(self, auth_headers):
        """Test duplicate email validation"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{unique_id}@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "active"
        }
        
        # Create first member
        response = client.post("/members/", json=member_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Try to create second member with same email
        member_data["first_name"] = "Jane"
        response = client.post("/members/", json=member_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]
    
    def test_unauthorized_access(self):
        """Test unauthorized access"""
        # Try to access without token
        response = client.get("/members/")
        assert response.status_code == 401
        
        response = client.post("/members/", json={})
        assert response.status_code == 401
    
    def test_not_found(self, auth_headers):
        """Test not found scenarios"""
        # Try to get non-existent member
        fake_id = str(uuid.uuid4())
        response = client.get(f"/members/{fake_id}", headers=auth_headers)
        assert response.status_code == 404
        
        # Try to update non-existent member
        response = client.patch(f"/members/{fake_id}", json={"team": 2}, headers=auth_headers)
        assert response.status_code == 404
        
        # Try to delete non-existent member
        response = client.delete(f"/members/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
