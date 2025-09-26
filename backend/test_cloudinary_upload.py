"""
Test script for Cloudinary upload utilities with error handling
"""

import sys
import os
sys.path.append('/home/itz_sensei/Documents/FypProject/backend')

from utils.cloudinary_upload import CloudinaryUploadManager, CloudinaryUploadError
from utils.cloudinary_errors import safe_upload_model, safe_upload_simulation, safe_delete_file, safe_get_download_url
import pickle
import tempfile

def test_upload_manager():
    """Test the CloudinaryUploadManager"""
    
    print("🧪 Testing Cloudinary Upload Manager...")
    
    # Initialize upload manager
    upload_manager = CloudinaryUploadManager()
    
    # Test 1: Create a dummy pickle file for model upload
    print("\n1. Testing model file upload...")
    
    # Create dummy model data
    dummy_model = {"type": "test_model", "accuracy": 0.95, "features": ["x", "y", "z"]}
    model_data = pickle.dumps(dummy_model)
    
    # Test with error handling wrapper
    result = safe_upload_model(
        upload_manager.upload_model_file,
        file_data=model_data,
        filename="test_model.pkl",
        user_id="test_user_123",
        model_name="Test ML Model"
    )
    
    if result['success']:
        data = result['data']
        print("✅ Model upload successful!")
        print(f"   Public ID: {data['public_id']}")
        print(f"   URL: {data['secure_url']}")
        print(f"   Size: {data['file_size']} bytes")
        
        # Test download URL generation with error handling
        url_result = safe_get_download_url(
            upload_manager.get_download_url,
            data['public_id']
        )
        
        if url_result['success']:
            print(f"   Download URL: {url_result['data']}")
        else:
            print(f"   Download URL failed: {url_result['message']}")
        
        # Clean up - delete the test file
        delete_result = safe_delete_file(upload_manager.delete_file, data['public_id'])
        if delete_result['success']:
            print("   Cleanup: ✅ Deleted")
        else:
            print(f"   Cleanup: ❌ Failed - {delete_result['message']}")
    else:
        print(f"❌ Model upload failed: {result['message']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    
    # Test 2: Test HTML simulation upload
    print("\n2. Testing simulation file upload...")
    
    # Create dummy HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Simulation</title></head>
    <body>
        <h1>Physics Simulation Results</h1>
        <p>This is a test simulation plot.</p>
        <script>
            console.log('Test simulation loaded');
        </script>
    </body>
    </html>
    """
    
    # Test with error handling wrapper
    result = safe_upload_simulation(
        upload_manager.upload_simulation_file,
        file_data=html_content,
        filename="test_simulation.html",
        user_id="test_user_123",
        simulation_name="Test Physics Simulation",
        file_type="html"
    )
    
    if result['success']:
        data = result['data']
        print("✅ Simulation upload successful!")
        print(f"   Public ID: {data['public_id']}")
        print(f"   URL: {data['secure_url']}")
        print(f"   Size: {data['file_size']} bytes")
        
        # Clean up - delete the test file
        delete_result = safe_delete_file(upload_manager.delete_file, data['public_id'])
        if delete_result['success']:
            print("   Cleanup: ✅ Deleted")
        else:
            print(f"   Cleanup: ❌ Failed - {delete_result['message']}")
    else:
        print(f"❌ Simulation upload failed: {result['message']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    
    # Test 3: Test file validation
    print("\n3. Testing file validation...")
    
    # Test file size limit
    large_data = b"x" * (60 * 1024 * 1024)  # 60MB - should exceed limit
    
    try:
        upload_manager.upload_model_file(
            file_data=large_data,
            filename="large_file.pkl",
            user_id="test_user_123",
            model_name="Large Test Model"
        )
        print("❌ Large file validation failed - should have been rejected")
    except CloudinaryUploadError as e:
        print(f"✅ Large file correctly rejected: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test invalid file type
    try:
        upload_manager.upload_model_file(
            file_data=b"test data",
            filename="invalid_file.txt",
            user_id="test_user_123",
            model_name="Invalid Test Model"
        )
        print("❌ Invalid file type validation failed - should have been rejected")
    except CloudinaryUploadError as e:
        print(f"✅ Invalid file type correctly rejected: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 Upload manager testing completed!")

if __name__ == "__main__":
    test_upload_manager()