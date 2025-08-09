#!/usr/bin/env python3
"""
Simple test script for Members API endpoints.
Run with: python test_members.py
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def get_auth_token(username: str = "testuser", password: str = "testpass") -> Optional[str]:
    """Get authentication token"""
    try:
        # First register a user
        register_data = {
            "email": f"{username}@example.com",
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"Registration failed: {response.status_code} - {response.text}")
            return None
        
        # Then login to get token
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_members_api():
    """Test all Members API endpoints"""
    print("Testing Members API...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Create a member
    print("\n1. Creating a member...")
    member_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "roles": ["player"],
        "team": 1,
        "status": "active",
        "notes": "Test member"
    }
    
    response = requests.post(f"{BASE_URL}/members/", json=member_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created_member = response.json()
        member_id = created_member["id"]
        print(f"Created member with ID: {member_id}")
        print(f"Member data: {json.dumps(created_member, indent=2)}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 2: Get the member
    print(f"\n2. Getting member {member_id}...")
    response = requests.get(f"{BASE_URL}/members/{member_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        member = response.json()
        print(f"Retrieved member: {json.dumps(member, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: List members with filters
    print("\n3. Listing members with filters...")
    response = requests.get(f"{BASE_URL}/members/?team=1&status=active", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        members_list = response.json()
        print(f"Found {members_list['total']} members")
        for member in members_list["members"]:
            print(f"  - {member['first_name']} {member['last_name']} (Team {member['team']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 4: Search members
    print("\n4. Searching members...")
    response = requests.get(f"{BASE_URL}/members/?q=john", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        search_results = response.json()
        print(f"Search found {search_results['total']} members")
        for member in search_results["members"]:
            print(f"  - {member['first_name']} {member['last_name']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Update member
    print(f"\n5. Updating member {member_id}...")
    update_data = {
        "team": 2,
        "notes": "Updated notes"
    }
    response = requests.patch(f"{BASE_URL}/members/{member_id}", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_member = response.json()
        print(f"Updated member: {json.dumps(updated_member, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 6: Create another member
    print("\n6. Creating another member...")
    member_data2 = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "roles": ["coach"],
        "team": 1,
        "status": "active"
    }
    
    response = requests.post(f"{BASE_URL}/members/", json=member_data2, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created_member2 = response.json()
        member_id2 = created_member2["id"]
        print(f"Created second member with ID: {member_id2}")
    else:
        print(f"Error: {response.text}")
        member_id2 = None
    
    # Test 7: List all members
    print("\n7. Listing all members...")
    response = requests.get(f"{BASE_URL}/members/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        all_members = response.json()
        print(f"Total members: {all_members['total']}")
        for member in all_members["members"]:
            print(f"  - {member['first_name']} {member['last_name']} ({', '.join(member['roles'])}) - Team {member['team']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 8: Soft delete member (optional - uncomment to test)
    if member_id2:
        print(f"\n8. Soft deleting member {member_id2}...")
        response = requests.delete(f"{BASE_URL}/members/{member_id2}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 204:
            print("Member soft deleted successfully")
        else:
            print(f"Error: {response.text}")
    
    print("\nMembers API test completed!")

if __name__ == "__main__":
    test_members_api()
