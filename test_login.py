#!/usr/bin/env python3

import requests
import json

# Test the login endpoint directly
def test_login():
    url = "http://localhost:5001/api/auth/login"
    
    # Test data
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {login_data}")
    
    try:
        # Create a session to handle cookies
        session = requests.Session()
        
        response = session.post(
            url, 
            json=login_data, 
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            
            # Test a protected endpoint
            print("\nTesting protected endpoint...")
            auth_check_response = session.get("http://localhost:5001/api/auth/check")
            print(f"Auth check status: {auth_check_response.status_code}")
            print(f"Auth check response: {auth_check_response.text}")
            
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_login()
