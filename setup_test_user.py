#!/usr/bin/env python3
"""
Setup test user and test authentication for document verification API
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'land_registration.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_user():
    """Create a test user if it doesn't exist"""
    username = 'testuser'
    email = 'test@example.com'
    password = 'testpass123'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists")
    else:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        print(f"Created user: {username}")
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"Created new token for user: {token.key}")
    else:
        print(f"Using existing token for user: {token.key}")
    
    return user, token

def test_authentication():
    """Test the authentication endpoint"""
    import requests
    
    # Test authentication endpoint
    auth_url = "http://localhost:8000/api/document-verification/auth/token/"
    
    # Test with correct credentials
    auth_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Authentication successful!")
            print(f"Access token: {token_data['access']}")
            print(f"User ID: {token_data['user_id']}")
            print(f"Username: {token_data['username']}")
            return token_data['access']
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running.")
        return None
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return None

def test_document_types():
    """Test getting document types"""
    import requests
    
    doc_types_url = "http://localhost:8000/api/document-verification/document-types/"
    
    try:
        response = requests.get(doc_types_url)
        if response.status_code == 200:
            doc_types = response.json()
            print("✅ Document types retrieved successfully!")
            print(f"Found {len(doc_types)} document types:")
            for doc_type in doc_types:
                print(f"  - {doc_type['name']}: {doc_type['description']}")
            return True
        else:
            print(f"❌ Failed to get document types: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing document types: {e}")
        return False

def main():
    """Main setup and test function"""
    print("🔧 Setting up test user and authentication...")
    print("=" * 50)
    
    try:
        # Create test user
        user, token = create_test_user()
        
        print("\n🧪 Testing API endpoints...")
        print("=" * 50)
        
        # Test authentication
        access_token = test_authentication()
        
        # Test document types
        test_document_types()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        
        if access_token:
            print(f"\n🔑 Your access token: {access_token}")
            print("\n📝 Use this token in Postman:")
            print("1. Set the 'auth_token' variable to the token above")
            print("2. Use 'Token {{auth_token}}' in the Authorization header")
            print("3. Test the API endpoints")
        
        print("\n🚀 Next steps:")
        print("1. Make sure Django server is running: python manage.py runserver")
        print("2. Import the Postman collection")
        print("3. Set the auth_token variable with the token above")
        print("4. Test the API endpoints")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 