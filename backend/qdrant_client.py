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
                elif response.status_code == 409:
                    logger.info(f"✅ Collection already exists: {collection_name}")
                    return True  # Collection exists, which is fine
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
                          limit: int = 5, score_threshold: float = 0.0, 
                          filter_conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors with optional filtering"""
        try:
            search_payload = {
                "vector": query_vector,
                "limit": limit,
                "with_payload": True,
                "score_threshold": score_threshold
            }
            
            # Add filter if provided
            if filter_conditions:
                search_payload["filter"] = filter_conditions
            
            # Use shorter timeout to prevent hanging
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.url}/collections/{collection_name}/points/search",
                    json=search_payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return results.get("result", [])
                else:
                    error_msg = f"Search failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return []
                    
        except asyncio.TimeoutError as e:
            logger.error(f"Search timeout: {e}")
            return []
        except httpx.TimeoutException as e:
            logger.error(f"HTTP timeout during search: {e}")
            return []
        except Exception as e:
            import traceback
            logger.error(f"Search error: {e}")
            logger.error(f"Search traceback: {traceback.format_exc()}")
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
    
    def __init__(self, qdrant_url: str, api_key: Optional[str] = None, embedding_service=None):
        self.qdrant = QdrantClient(qdrant_url, api_key)
        self.collection_name = "physics_knowledge"
        self.embedding_service = embedding_service
        self._initialize_embedding_service()
    
    def _initialize_embedding_service(self):
        """Initialize Google embedding service for consistency with indexing"""
        if self.embedding_service is None:
            try:
                # Try different import paths for embedding service
                embedding_service = None
                
                # Try package import first
                try:
                    from backend.ai.embedding_service import get_embedding_service
                    embedding_service = get_embedding_service()
                    logger.info("✅ Embedding service imported from backend.ai.embedding_service")
                except ImportError:
                    # Try direct import
                    try:
                        from ai.embedding_service import get_embedding_service
                        embedding_service = get_embedding_service()
                        logger.info("✅ Embedding service imported from ai.embedding_service")
                    except ImportError:
                        logger.warning("⚠️ Could not import embedding service from either path")
                        
                if embedding_service:
                    self.embedding_service = embedding_service
                    logger.info("✅ Embedding service initialized with model: text-embedding-004")
                else:
                    self.embedding_service = None
                    logger.warning("⚠️ Embedding service could not be initialized")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize embedding service: {e}")
                logger.info("🔧 No embedding model - will accept pre-computed embeddings")
                self.embedding_service = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google's text-embedding-004"""
        if self.embedding_service:
            result = await self.embedding_service.generate_single_embedding(text)
            if result.error:
                raise ValueError(f"Embedding generation failed: {result.error}")
            return result.embedding
        else:
            raise ValueError("No embedding service available - please provide pre-computed embeddings")
    
    async def initialize(self) -> bool:
        """Initialize the physics vector database"""
        try:
            # Check if Qdrant is healthy
            if not await self.qdrant.health_check():
                logger.error("❌ Qdrant service is not healthy")
                return False
            
            # Create physics collection with 768 dimensions (Google text-embedding-004)
            success = await self.qdrant.create_collection(self.collection_name, 768)
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
                elif self.embedding_service:
                    vector = await self.generate_embedding(searchable_text)
                else:
                    logger.error("No embedding provided and no service available")
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
                                   score_threshold: float = 0.3,
                                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for physics content with optional filtering"""
        try:
            logger.info(f"🔍 Starting search for query: '{query[:50]}...' with filters: {filters}")
            
            # Generate query embedding using Google's text-embedding-004
            if self.embedding_service:
                logger.info("📊 Generating embedding for query...")
                query_vector = await self.generate_embedding(query)
                logger.info(f"✅ Generated embedding vector of size: {len(query_vector)}")
            else:
                error_msg = "No embedding service available for query"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Build Qdrant filter conditions
            filter_conditions = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    # Handle metadata fields (user_id is in metadata)
                    if key in ['user_id', 'material_id']:
                        conditions.append({
                            'key': f'metadata.{key}',
                            'match': {'value': value}
                        })
                    else:
                        conditions.append({
                            'key': key,
                            'match': {'value': value}
                        })
                
                if conditions:
                    filter_conditions = {'must': conditions}
                    logger.info(f"🔧 Applied filter conditions: {filter_conditions}")
            
            # Search in Qdrant
            logger.info(f"🔍 Searching in Qdrant collection '{self.collection_name}'...")
            results = await self.qdrant.search_points(
                self.collection_name, 
                query_vector, 
                limit, 
                score_threshold,
                filter_conditions
            )
            logger.info(f"✅ Qdrant search returned {len(results)} results")
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    'id': result['id'],
                    'score': result['score'],
                    **result['payload']
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"✅ Search completed successfully: {len(formatted_results)} formatted results")
            return formatted_results
            
        except Exception as e:
            import traceback
            logger.error(f"Search failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
def create_physics_vector_db(qdrant_url: str = None, api_key: str = None, embedding_service=None) -> PhysicsVectorDB:
    """Create physics vector database instance"""
    
    # Get URL from environment if not provided
    if not qdrant_url:
        qdrant_url = os.getenv('QDRANT_URL')
        if not qdrant_url:
            raise ValueError("QDRANT_URL not provided and not found in environment")
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('QDRANT_API_KEY')  # Optional
    
    return PhysicsVectorDB(qdrant_url, api_key, embedding_service)

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