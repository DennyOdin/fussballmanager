#!/usr/bin/env python3
"""
Simple test to verify Members API is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_members_api():
    """Test the Members API endpoints"""
    print("Testing Members API...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code != 200:
            print("Server not running properly")
            return
    except Exception as e:
        print(f"Server not accessible: {e}")
        return
    
    # Test 2: Register a user
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register: {response.status_code}")
    
    # Test 3: Login
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 4: Create a member
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "roles": ["player"],
            "team": 1,
            "status": "active"
        }
        
        response = requests.post(f"{BASE_URL}/members/", json=member_data, headers=headers)
        print(f"Create member: {response.status_code}")
        
        if response.status_code == 201:
            created_member = response.json()
            member_id = created_member["id"]
            print(f"Created member ID: {member_id}")
            
            # Test 5: Get member
            response = requests.get(f"{BASE_URL}/members/{member_id}", headers=headers)
            print(f"Get member: {response.status_code}")
            
            # Test 6: List members
            response = requests.get(f"{BASE_URL}/members/", headers=headers)
            print(f"List members: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Total members: {data['total']}")
            
            # Test 7: Update member
            update_data = {"team": 2}
            response = requests.patch(f"{BASE_URL}/members/{member_id}", json=update_data, headers=headers)
            print(f"Update member: {response.status_code}")
            
            # Test 8: Delete member
            response = requests.delete(f"{BASE_URL}/members/{member_id}", headers=headers)
            print(f"Delete member: {response.status_code}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_members_api()
