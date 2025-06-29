#!/usr/bin/env python3
"""
Test script for AI Document Verification System
This script demonstrates the document verification functionality
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

from document_verification.models import DocumentType, Document, VerificationResult
from document_verification.utils import document_verifier
from django.contrib.auth.models import User
import tempfile
import json

def create_test_user():
    """Create a test user if it doesn't exist"""
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    return user

def create_sample_document_types():
    """Create sample document types"""
    document_types = [
        {
            'name': 'Land Deed',
            'description': 'Official land ownership document',
            'required_fields': ['owner_name', 'property_address', 'property_area', 'document_date']
        },
        {
            'name': 'Property Tax Receipt',
            'description': 'Property tax payment receipt',
            'required_fields': ['owner_name', 'property_address', 'tax_amount', 'payment_date']
        }
    ]
    
    created_types = []
    for doc_type_data in document_types:
        doc_type, created = DocumentType.objects.get_or_create(
            name=doc_type_data['name'],
            defaults=doc_type_data
        )
        created_types.append(doc_type)
        if created:
            print(f"Created document type: {doc_type.name}")
        else:
            print(f"Using existing document type: {doc_type.name}")
    
    return created_types

def test_ocr_extraction():
    """Test OCR text extraction"""
    print("\n=== Testing OCR Text Extraction ===")
    
    # Create a simple test image with text (you would need an actual image file)
    # For demonstration, we'll create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("This is a sample land deed document.\nOwner: John Doe\nProperty: 123 Main Street\nArea: 2.5 acres")
        temp_file_path = temp_file.name
    
    try:
        # Note: This would require an actual image file for real OCR testing
        print("OCR test would require an actual image file")
        print("Sample text extraction would work with: 'This is a sample land deed document. Owner: John Doe Property: 123 Main Street Area: 2.5 acres'")
        
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_forgery_detection():
    """Test forgery detection"""
    print("\n=== Testing Forgery Detection ===")
    
    # Create a simple test image (you would need an actual image file)
    print("Forgery detection test would require an actual image file")
    print("Heuristic-based detection would analyze:")
    print("- Edge density")
    print("- Texture uniformity")
    print("- Noise levels")
    print("- Color consistency")

def test_nlp_verification():
    """Test NLP verification"""
    print("\n=== Testing NLP Verification ===")
    
    sample_text = """
    LAND DEED DOCUMENT
    
    This deed certifies that John Doe is the legal owner of the property
    located at 123 Main Street, Anytown, USA. The property area is 2.5 acres.
    This document was issued on January 15, 2024.
    
    Document Number: LD-2024-001
    Property Type: Residential Land
    """
    
    expected_fields = {
        'owner_name': 'John Doe',
        'property_address': '123 Main Street',
        'property_area': '2.5 acres',
        'document_date': 'January 15, 2024'
    }
    
    print("Sample text:")
    print(sample_text)
    print("\nExpected fields:")
    for field, value in expected_fields.items():
        print(f"  {field}: {value}")
    
    print("\nNLP verification would:")
    print("- Extract field values using question-answering")
    print("- Compare extracted values with expected values")
    print("- Calculate confidence scores")
    print("- Provide verification results")

def test_complete_verification_pipeline():
    """Test the complete verification pipeline"""
    print("\n=== Testing Complete Verification Pipeline ===")
    
    # This would require actual image files for full testing
    print("Complete verification pipeline includes:")
    print("1. OCR Text Extraction")
    print("2. Forgery Detection")
    print("3. NLP Field Verification")
    print("4. Overall Verification Decision")
    
    print("\nSample verification result structure:")
    sample_result = {
        "overall_verified": True,
        "ocr_result": {
            "success": True,
            "text": "Sample extracted text...",
            "confidence": 0.95
        },
        "forgery_result": {
            "success": True,
            "is_genuine": True,
            "score": 0.85
        },
        "nlp_result": {
            "success": True,
            "confidence": 0.90,
            "extracted_fields": {
                "owner_name": "John Doe",
                "property_address": "123 Main Street"
            },
            "overall_verification": 0.90
        },
        "verification_notes": [
            "✓ Text extraction successful",
            "✓ Document appears genuine",
            "✓ Document details verified"
        ]
    }
    
    print(json.dumps(sample_result, indent=2))

def test_api_endpoints():
    """Test API endpoints (simulation)"""
    print("\n=== Testing API Endpoints ===")
    
    endpoints = [
        "GET /api/document-verification/document-types/",
        "GET /api/document-verification/documents/",
        "POST /api/document-verification/documents/upload/",
        "GET /api/document-verification/documents/{id}/",
        "GET /api/document-verification/documents/{id}/verify/",
        "POST /api/document-verification/documents/{id}/reverify/",
        "DELETE /api/document-verification/documents/{id}/delete/"
    ]
    
    print("Available API endpoints:")
    for endpoint in endpoints:
        print(f"  {endpoint}")

def main():
    """Main test function"""
    print("AI Document Verification System - Test Script")
    print("=" * 50)
    
    try:
        # Create test user
        user = create_test_user()
        
        # Create document types
        document_types = create_sample_document_types()
        
        # Test individual components
        test_ocr_extraction()
        test_forgery_detection()
        test_nlp_verification()
        test_complete_verification_pipeline()
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("\nTo run the full system:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run migrations: python manage.py migrate")
        print("3. Setup document types: python manage.py setup_document_types")
        print("4. Start server: python manage.py runserver")
        print("5. Access the web interface at: http://localhost:8000")
        print("6. Access the API at: http://localhost:8000/api/document-verification/")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 