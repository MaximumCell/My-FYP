"""
Simple test to create a user and verify MongoDB collection creation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.database import get_database
from models.user import UserCreate, UserService

def test_user_creation():
    """Test creating a user to verify collection creation"""
    try:
        print("🔍 Testing user creation...")
        
        # Get database connection
        db = get_database()
        print(f"✅ Connected to database: {db.name}")
        
        # Create user service
        user_service = UserService(db)
        print("✅ User service initialized")
        
        # Create a test user
        test_user_data = UserCreate(
            clerk_user_id="test_clerk_123",
            email="test@example.com",
            name="Test User"
        )
        
        print("Creating test user...")
        synced_user = user_service.sync_user(test_user_data)
        
        if synced_user:
            print(f"✅ User created successfully!")
            print(f"   - ID: {synced_user.id}")
            print(f"   - Name: {synced_user.name}")
            print(f"   - Email: {synced_user.email}")
            print(f"   - Clerk ID: {synced_user.clerk_user_id}")
            
            # Check if collection exists now
            collections = db.list_collection_names()
            print(f"✅ Collections in database: {collections}")
            
            # Count documents
            user_count = db.users.count_documents({})
            print(f"✅ Total users in collection: {user_count}")
            
            return True
        else:
            print("❌ Failed to create user")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing MongoDB Collection Creation")
    print("=" * 50)
    
    success = test_user_creation()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("Check your MongoDB Atlas dashboard - you should now see the 'users' collection.")
    else:
        print("\n❌ Test failed. Please check the errors above.")