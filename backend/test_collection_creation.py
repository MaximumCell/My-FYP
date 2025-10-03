#!/usr/bin/env python3
"""
Test script to create the Qdrant collection
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

async def test_collection_creation():
    """Test creating the Qdrant collection"""
    print("🧪 Testing Qdrant collection creation...")
    
    try:
        # Import the physics vector DB
        from qdrant_client import create_physics_vector_db
        
        qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
        qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
        
        print(f"📡 Connecting to Qdrant at: {qdrant_url}")
        
        # Create the physics vector database
        vector_db = create_physics_vector_db(qdrant_url, qdrant_api_key)
        
        # Initialize the collection
        print("🔧 Initializing collection...")
        success = await vector_db.initialize()
        
        if success:
            print("✅ Collection 'physics_knowledge' created successfully!")
            
            # Get collection info
            stats = await vector_db.get_stats()
            print(f"📊 Collection stats: {stats}")
        else:
            print("❌ Failed to create collection")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_collection_creation())