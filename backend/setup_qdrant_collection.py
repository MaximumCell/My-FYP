"""
Setup Qdrant Collection for Physics Knowledge
Creates the physics_knowledge collection with correct vector dimensions
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', '')
VECTOR_DIMENSION = 768  # Google text-embedding-004 dimension

async def create_physics_collection():
    """Create the physics_knowledge collection"""
    
    collection_name = "physics_knowledge"
    
    collection_config = {
        "vectors": {
            "size": VECTOR_DIMENSION,
            "distance": "Cosine"
        }
    }
    
    headers = {}
    if QDRANT_API_KEY:
        headers['api-key'] = QDRANT_API_KEY
    
    print(f"🔄 Creating collection '{collection_name}' at {QDRANT_URL}...")
    print(f"   Vector dimension: {VECTOR_DIMENSION}")
    print(f"   Distance metric: Cosine")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check if collection exists
            check_response = await client.get(
                f"{QDRANT_URL}/collections/{collection_name}",
                headers=headers
            )
            
            if check_response.status_code == 200:
                print(f"✅ Collection '{collection_name}' already exists!")
                
                # Get collection info
                info = check_response.json()
                vector_size = info['result']['config']['params']['vectors']['size']
                print(f"   Current vector size: {vector_size}")
                
                if vector_size != VECTOR_DIMENSION:
                    print(f"⚠️  WARNING: Collection has different vector size ({vector_size} vs {VECTOR_DIMENSION})")
                    print(f"   You may need to delete and recreate the collection")
                
                return True
            
            # Create collection
            create_response = await client.put(
                f"{QDRANT_URL}/collections/{collection_name}",
                json=collection_config,
                headers=headers
            )
            
            if create_response.status_code in [200, 201]:
                print(f"✅ Successfully created collection '{collection_name}'!")
                return True
            else:
                print(f"❌ Failed to create collection: {create_response.status_code}")
                print(f"   Response: {create_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def verify_collection():
    """Verify the collection was created correctly"""
    
    collection_name = "physics_knowledge"
    
    headers = {}
    if QDRANT_API_KEY:
        headers['api-key'] = QDRANT_API_KEY
    
    print(f"\n🔍 Verifying collection '{collection_name}'...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{QDRANT_URL}/collections/{collection_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                info = response.json()['result']
                print(f"✅ Collection verified!")
                print(f"   Status: {info['status']}")
                print(f"   Vectors count: {info['vectors_count']}")
                print(f"   Points count: {info['points_count']}")
                print(f"   Vector size: {info['config']['params']['vectors']['size']}")
                return True
            else:
                print(f"❌ Collection not found or error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

async def main():
    print("=" * 60)
    print("Qdrant Physics Knowledge Collection Setup")
    print("=" * 60)
    
    # Create collection
    success = await create_physics_collection()
    
    if success:
        # Verify it was created
        await verify_collection()
        print("\n✅ Setup complete! You can now upload materials and they will be indexed.")
    else:
        print("\n❌ Setup failed. Please check your Qdrant configuration.")
        print(f"   QDRANT_URL: {QDRANT_URL}")
        print(f"   QDRANT_API_KEY: {'Set' if QDRANT_API_KEY else 'Not set'}")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
