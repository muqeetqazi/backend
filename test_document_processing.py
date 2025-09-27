#!/usr/bin/env python
"""
Test script to verify document processing works correctly
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_document_processing():
    """
    Test document processing with cURL-like requests
    """
    print("🧪 Testing Document Processing...")
    
    # Test configuration
    BASE_URL = "https://protected-vision-soh4o.ondigitalocean.app/api"
    # You'll need to replace these with actual values
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("📋 Test Steps:")
    print("1. Get current user profile")
    print("2. Upload a test document")
    print("3. Check document status")
    print("4. Mark document as processed")
    print("5. Verify document is processed")
    print("6. Check updated user stats")
    
    # Step 1: Get current profile
    print("\n1️⃣ Getting current user profile...")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Current stats: {profile['total_documents_processed']} processed")
        else:
            print(f"❌ Failed to get profile: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return
    
    # Step 2: Upload test document
    print("\n2️⃣ Uploading test document...")
    try:
        # Create a simple test file
        test_file_content = b"Test document content for processing"
        files = {
            'file': ('test_document.txt', test_file_content, 'text/plain')
        }
        data = {
            'title': 'Test Processing Document',
            'file_type': 'image'
        }
        
        upload_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.post(f"{BASE_URL}/documents/", headers=upload_headers, files=files, data=data)
        
        if response.status_code == 201:
            document = response.json()
            document_id = document['id']
            print(f"✅ Document uploaded with ID: {document_id}")
            print(f"   Initial processed status: {document['processed']}")
        else:
            print(f"❌ Failed to upload document: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return
    
    # Step 3: Check document status
    print("\n3️⃣ Checking document status...")
    try:
        response = requests.get(f"{BASE_URL}/documents/{document_id}/", headers=headers)
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document status: processed={document['processed']}")
        else:
            print(f"❌ Failed to get document: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting document: {e}")
    
    # Step 4: Mark document as processed
    print("\n4️⃣ Marking document as processed...")
    try:
        update_data = {"processed": True}
        response = requests.patch(f"{BASE_URL}/documents/{document_id}/", headers=headers, json=update_data)
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document updated successfully!")
            print(f"   New processed status: {document['processed']}")
        else:
            print(f"❌ Failed to update document: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error updating document: {e}")
        return
    
    # Step 5: Verify document is processed
    print("\n5️⃣ Verifying document is processed...")
    try:
        response = requests.get(f"{BASE_URL}/documents/{document_id}/", headers=headers)
        if response.status_code == 200:
            document = response.json()
            if document['processed']:
                print(f"✅ SUCCESS: Document is now processed!")
            else:
                print(f"❌ FAILED: Document is still not processed")
        else:
            print(f"❌ Failed to verify document: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying document: {e}")
    
    # Step 6: Check updated user stats
    print("\n6️⃣ Checking updated user stats...")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Updated stats:")
            print(f"   Documents processed: {profile['total_documents_processed']}")
            print(f"   Documents saved: {profile['total_documents_saved']}")
        else:
            print(f"❌ Failed to get updated profile: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updated profile: {e}")
    
    print("\n🎉 Test completed!")

def test_with_curl_commands():
    """
    Print the exact cURL commands to test manually
    """
    print("\n📋 Manual Testing with cURL:")
    print("=" * 50)
    
    print("\n1. Get your access token first:")
    print("curl -X POST 'https://protected-vision-soh4o.ondigitalocean.app/api/auth/login/' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"email\": \"your-email@example.com\", \"password\": \"your-password\"}'")
    
    print("\n2. Upload a document:")
    print("curl -X POST 'https://protected-vision-soh4o.ondigitalocean.app/api/documents/' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\")
    print("  -F 'title=Test Document' \\")
    print("  -F 'file_type=image' \\")
    print("  -F 'file=@test_image.jpg'")
    
    print("\n3. Check document status:")
    print("curl -X GET 'https://protected-vision-soh4o.ondigitalocean.app/api/documents/1/' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'")
    
    print("\n4. Mark document as processed (THIS SHOULD NOW WORK):")
    print("curl -X PATCH 'https://protected-vision-soh4o.ondigitalocean.app/api/documents/1/' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"processed\": true}'")
    
    print("\n5. Verify document is processed:")
    print("curl -X GET 'https://protected-vision-soh4o.ondigitalocean.app/api/documents/1/' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'")
    
    print("\n6. Check updated user stats:")
    print("curl -X GET 'https://protected-vision-soh4o.ondigitalocean.app/api/auth/profile/' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'")

if __name__ == "__main__":
    print("🔧 Document Processing Test")
    print("=" * 30)
    
    # Show manual testing commands
    test_with_curl_commands()
    
    # Uncomment the line below to run automated tests (requires valid token)
    # test_document_processing()
