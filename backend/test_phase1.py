"""
Test script for Phase 1: Database Integration
Run this to test MongoDB connection and User model functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Test imports (will fail if packages not installed)
try:
    from utils.database import init_database, get_database, close_database
    from models.user import UserCreate, UserService
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip install pymongo python-dotenv pydantic")
    sys.exit(1)

def test_database_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing database connection...")
    try:
        if init_database():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def test_user_operations():
    """Test user CRUD operations"""
    print("\n🔍 Testing user operations...")
    try:
        # Get database and user service
        db = get_database()
        user_service = UserService(db)
        
        # Test user creation
        test_user_data = UserCreate(
            clerk_user_id="test_user_123",
            email="test@example.com",
            name="Test User"
        )
        
        print("Creating test user...")
        synced_user = user_service.sync_user(test_user_data)
        
        if synced_user:
            print(f"✅ User created/synced: {synced_user.name} ({synced_user.email})")
            
            # Test user retrieval
            retrieved_user = user_service.get_user_by_clerk_id("test_user_123")
            if retrieved_user:
                print(f"✅ User retrieved: {retrieved_user.name}")
            else:
                print("❌ Failed to retrieve user")
                return False
            
            # Test analytics update
            analytics_update = {
                "total_models_trained": 5,
                "total_simulations_run": 3,
                "total_training_time": 1200
            }
            
            success = user_service.update_usage_analytics("test_user_123", analytics_update)
            if success:
                print("✅ Analytics updated successfully")
            else:
                print("❌ Failed to update analytics")
            
            # Cleanup test user
            db.users.delete_one({"clerk_user_id": "test_user_123"})
            print("✅ Test user cleaned up")
            
            return True
        else:
            print("❌ Failed to create/sync user")
            return False
            
    except Exception as e:
        print(f"❌ User operations error: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints (requires Flask app running)"""
    print("\n🔍 Testing API endpoints...")
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test user sync endpoint
        sync_data = {
            "clerk_user_id": "api_test_user_456",
            "email": "apitest@example.com",
            "name": "API Test User"
        }
        
        sync_response = requests.post(f"{base_url}/api/users/sync", json=sync_data, timeout=10)
        if sync_response.status_code == 200:
            print("✅ User sync endpoint working")
            
            # Test dashboard endpoint
            dashboard_response = requests.get(
                f"{base_url}/api/users/dashboard",
                params={"clerk_user_id": "api_test_user_456"},
                timeout=10
            )
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard endpoint working")
                return True
            else:
                print(f"❌ Dashboard endpoint failed: {dashboard_response.status_code}")
        else:
            print(f"❌ User sync endpoint failed: {sync_response.status_code}")
            
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test error: {str(e)}")
        print("Note: Make sure Flask app is running on localhost:5000")
        return False
    except ImportError:
        print("❌ requests library not installed. Skipping API tests.")
        print("Install with: pip install requests")
        return True  # Don't fail the test for missing requests

def main():
    """Run all tests"""
    print("🚀 Starting Phase 1 Database Integration Tests")
    print("=" * 50)
    
    # Test 1: Database connection
    db_success = test_database_connection()
    
    # Test 2: User operations (only if DB connection works)
    user_success = False
    if db_success:
        user_success = test_user_operations()
    
    # Test 3: API endpoints (optional)
    api_success = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print(f"Database Connection: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"User Operations: {'✅ PASS' if user_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL (optional)'}")
    
    if db_success and user_success:
        print("\n🎉 Phase 1 implementation is working correctly!")
        print("Ready to proceed to Phase 2: Cloudinary Integration")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    # Cleanup
    close_database()

if __name__ == "__main__":
    main()