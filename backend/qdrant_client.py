"""
Simple Qdrant Vector Database Client
===================================

A lightweight client for Qdrant vector database deployed on Render.
No heavy dependencies - just HTTP requests!
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Only need these basic packages (already in your requirements)
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class QdrantClient:
    """Simple HTTP client for Qdrant vector database"""
    
    def __init__(self, url: str, api_key: Optional[str] = None):
        """
        Initialize Qdrant client
        
        Args:
            url: Qdrant service URL (e.g., https://your-service.onrender.com)
            api_key: Optional API key for authentication
        """
        self.url = url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["api-key"] = api_key
    
    async def health_check(self) -> bool:
        """Check if Qdrant service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.url}/")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        """Create a collection for vectors"""
        try:
            collection_config = {
                "vectors": {
                    "size": vector_size,
                    "distance": "Cosine"
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.url}/collections/{collection_name}",
                    json=collection_config,
                    headers=self.headers
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Created collection: {collection_name}")
                    return True
                else:
                    logger.error(f"Failed to create collection: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    async def add_points(self, collection_name: str, points: List[Dict[str, Any]]) -> bool:
        """Add points (vectors with metadata) to collection"""
        try:
            payload = {"points": points}
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.put(
                    f"{self.url}/collections/{collection_name}/points",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Added {len(points)} points to {collection_name}")
                    return True
                else:
                    logger.error(f"Failed to add points: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            return False
    
    async def search_points(self, collection_name: str, query_vector: List[float], 
                          limit: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            search_payload = {
                "vector": query_vector,
                "limit": limit,
                "with_payload": True,
                "score_threshold": score_threshold
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.url}/collections/{collection_name}/points/search",
                    json=search_payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return results.get("result", [])
                else:
                    logger.error(f"Search failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def delete_points(self, collection_name: str, point_ids: List[str]) -> bool:
        """Delete points by IDs"""
        try:
            payload = {"points": point_ids}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.url}/collections/{collection_name}/points/delete",
                    json=payload,
                    headers=self.headers
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error deleting points: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.url}/collections/{collection_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()["result"]
                return None
                
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None

class PhysicsVectorDB:
    """Physics-specific vector database using Qdrant"""
    
    def __init__(self, qdrant_url: str, api_key: Optional[str] = None):
        self.qdrant = QdrantClient(qdrant_url, api_key)
        self.collection_name = "physics_knowledge"
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize a simple embedding model (optional - you can generate embeddings externally)"""
        try:
            # Only import if needed - fallback to external embedding generation
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded")
        except ImportError:
            logger.info("🔧 No embedding model - will accept pre-computed embeddings")
            self.embedding_model = None
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (if model is available)"""
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()
        else:
            raise ValueError("No embedding model available - please provide pre-computed embeddings")
    
    async def initialize(self) -> bool:
        """Initialize the physics vector database"""
        try:
            # Check if Qdrant is healthy
            if not await self.qdrant.health_check():
                logger.error("❌ Qdrant service is not healthy")
                return False
            
            # Create physics collection
            success = await self.qdrant.create_collection(self.collection_name, 384)
            if success:
                logger.info("✅ Physics vector database initialized")
                return True
            else:
                logger.error("❌ Failed to create physics collection")
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def add_physics_content(self, physics_items: List[Dict[str, Any]]) -> bool:
        """Add physics content to vector database"""
        try:
            points = []
            
            for i, item in enumerate(physics_items):
                # Create searchable text
                text_parts = []
                if 'content' in item:
                    content = item['content']
                    if isinstance(content, dict):
                        text_parts.extend([
                            content.get('title', ''),
                            content.get('concept_explanation', ''),
                            ' '.join(content.get('key_formulas', [])),
                        ])
                    else:
                        text_parts.append(str(content))
                
                text_parts.extend([
                    item.get('topic', ''),
                    item.get('subtopic', ''),
                ])
                
                searchable_text = ' '.join(filter(None, text_parts))
                
                # Generate embedding
                if 'embedding' in item:
                    vector = item['embedding']
                elif self.embedding_model:
                    vector = self.generate_embedding(searchable_text)
                else:
                    logger.error("No embedding provided and no model available")
                    return False
                
                # Create point
                point = {
                    "id": item.get('_id', f"physics_{i}_{int(datetime.now().timestamp())}"),
                    "vector": vector,
                    "payload": {
                        **item,
                        "searchable_text": searchable_text,
                        "created_at": datetime.now().isoformat()
                    }
                }
                points.append(point)
            
            return await self.qdrant.add_points(self.collection_name, points)
            
        except Exception as e:
            logger.error(f"Failed to add physics content: {e}")
            return False
    
    async def search_physics_content(self, query: str, limit: int = 5, 
                                   score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for physics content"""
        try:
            # Generate query embedding
            if self.embedding_model:
                query_vector = self.generate_embedding(query)
            else:
                raise ValueError("No embedding model available for query")
            
            # Search in Qdrant
            results = await self.qdrant.search_points(
                self.collection_name, 
                query_vector, 
                limit, 
                score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    'id': result['id'],
                    'score': result['score'],
                    **result['payload']
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            info = await self.qdrant.get_collection_info(self.collection_name)
            if info:
                return {
                    'backend': 'qdrant',
                    'collection': self.collection_name,
                    'points_count': info.get('points_count', 0),
                    'vectors_count': info.get('vectors_count', 0),
                    'status': info.get('status', 'unknown')
                }
            return {'backend': 'qdrant', 'status': 'unknown'}
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'backend': 'qdrant', 'status': 'error', 'error': str(e)}

# Simple factory function
def create_physics_vector_db(qdrant_url: str = None, api_key: str = None) -> PhysicsVectorDB:
    """Create physics vector database instance"""
    
    # Get URL from environment if not provided
    if not qdrant_url:
        qdrant_url = os.getenv('QDRANT_URL')
        if not qdrant_url:
            raise ValueError("QDRANT_URL not provided and not found in environment")
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('QDRANT_API_KEY')  # Optional
    
    return PhysicsVectorDB(qdrant_url, api_key)

# Example usage and testing
async def test_qdrant_deployment():
    """Test the Qdrant deployment"""
    print("🧪 Testing Qdrant Vector Database")
    print("=" * 50)
    
    # You'll need to set these after deployment
    qdrant_url = os.getenv('QDRANT_URL', 'https://your-qdrant-service.onrender.com')
    
    try:
        # Create physics vector DB
        db = create_physics_vector_db(qdrant_url)
        
        # Initialize
        print("🔧 Initializing physics vector database...")
        success = await db.initialize()
        
        if not success:
            print("❌ Failed to initialize - check your Qdrant deployment")
            return
        
        # Test with sample physics content
        sample_content = [
            {
                "_id": "newton_first_law",
                "topic": "mechanics",
                "subtopic": "newton_laws",
                "content": {
                    "title": "Newton's First Law of Motion",
                    "concept_explanation": "An object at rest stays at rest and an object in motion stays in motion unless acted upon by an unbalanced force.",
                    "key_formulas": ["ΣF = 0"],
                }
            }
        ]
        
        print("📝 Adding sample physics content...")
        add_success = await db.add_physics_content(sample_content)
        
        if add_success:
            print("✅ Content added successfully")
            
            # Test search
            print("🔍 Testing search...")
            results = await db.search_physics_content("force and motion", limit=2)
            
            if results:
                print(f"✅ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    title = result.get('content', {}).get('title', 'Unknown')
                    score = result.get('score', 0)
                    print(f"   {i}. {title} (score: {score:.3f})")
            else:
                print("⚠️ No results found")
            
            # Get stats
            stats = await db.get_stats()
            print(f"📊 Database stats: {stats}")
            
        else:
            print("❌ Failed to add content")
        
        print("✅ Qdrant test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_qdrant_deployment())