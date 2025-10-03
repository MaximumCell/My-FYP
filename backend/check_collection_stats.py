#!/usr/bin/env python3
"""
Check Qdrant collection stats
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

async def check_collection_stats():
    """Check the Qdrant collection stats"""
    print("📊 Checking Qdrant collection stats...")
    
    try:
        # Import the physics vector DB
        from qdrant_client import create_physics_vector_db
        
        qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
        qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
        
        print(f"📡 Connecting to Qdrant at: {qdrant_url}")
        
        # Create the physics vector database
        vector_db = create_physics_vector_db(qdrant_url, qdrant_api_key)
        
        # Get collection info
        print("📊 Getting collection stats...")
        stats = await vector_db.get_stats()
        print(f"📊 Collection stats: {stats}")
        
        # Try to get collection info directly
        collection_info = await vector_db.qdrant.get_collection_info("physics_knowledge")
        if collection_info:
            print(f"📊 Raw collection info: {collection_info}")
        else:
            print("❌ Could not get collection info")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_collection_stats())