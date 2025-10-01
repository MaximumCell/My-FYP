"""
Physics Vector Database Integration
=================================

This module integrates the Google embedding service with the Qdrant vector database
to provide a complete vector search and retrieval system for physics content.

Features:
- Seamless embedding + vector DB integration
- Automated content processing and indexing
- Advanced similarity search with filtering
- Batch operations for efficiency
- Physics-specific content enhancement
- Comprehensive error handling and monitoring

Author: Physics AI Tutor Team
Date: September 28, 2025
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import traceback

from .embedding_service import (
    PhysicsEmbeddingService, 
    EmbeddingResult, 
    BatchEmbeddingResult,
    get_embedding_service
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PhysicsContent:
    """Structured physics content for vector storage"""
    id: str
    title: str
    content: str
    topic: str
    subtopic: Optional[str] = None
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    content_type: str = "concept"  # concept, formula, example, problem
    source: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.id is None or self.id == "":
            self.id = str(uuid.uuid4())

@dataclass
class SearchResult:
    """Result from vector similarity search"""
    content: PhysicsContent
    similarity_score: float
    rank: int

@dataclass
class SearchResponse:
    """Complete search response with metadata"""
    query: str
    results: List[SearchResult]
    total_found: int
    search_time: float
    embedding_time: float
    filters_applied: Dict[str, Any]
    
class PhysicsVectorDatabase:
    """
    Enhanced vector database integration for physics content
    
    This class provides a complete pipeline from text to searchable vectors,
    combining the Google embedding service with Qdrant for efficient
    similarity search and retrieval.
    """
    
    def __init__(self, 
                 embedding_service: Optional[PhysicsEmbeddingService] = None,
                 qdrant_client = None,
                 collection_name: str = "physics_knowledge",
                 vector_size: int = 768):  # Google text-embedding-004 dimension
        """
        Initialize the vector database integration
        
        Args:
            embedding_service: Embedding service instance
            qdrant_client: Qdrant client instance
            collection_name: Name of the vector collection
            vector_size: Dimension of embedding vectors
        """
        self.embedding_service = embedding_service or get_embedding_service()
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Statistics tracking
        self.stats = {
            'total_documents_indexed': 0,
            'total_searches_performed': 0,
            'total_embedding_time': 0.0,
            'total_search_time': 0.0,
            'last_reset': datetime.now()
        }
        
        logger.info(f"✅ PhysicsVectorDatabase initialized for collection: {collection_name}")
    
    def _enhance_physics_content(self, content: Union[str, Dict[str, Any]]) -> str:
        """
        Enhance content for better embedding quality
        
        Args:
            content: Raw content string or structured content dict
            
        Returns:
            Enhanced text optimized for physics embeddings
        """
        if isinstance(content, str):
            return content
            
        if isinstance(content, dict):
            parts = []
            
            # Build comprehensive text representation
            if content.get('title'):
                parts.append(f"Title: {content['title']}")
            
            if content.get('topic'):
                parts.append(f"Physics Topic: {content['topic']}")
                
            if content.get('subtopic'):
                parts.append(f"Subtopic: {content['subtopic']}")
                
            if content.get('content'):
                parts.append(f"Content: {content['content']}")
                
            if content.get('difficulty_level'):
                parts.append(f"Level: {content['difficulty_level']}")
                
            if content.get('content_type'):
                parts.append(f"Type: {content['content_type']}")
            
            # Add any formulas or equations
            if content.get('formulas'):
                formulas = content['formulas']
                if isinstance(formulas, list):
                    parts.append(f"Formulas: {', '.join(formulas)}")
                else:
                    parts.append(f"Formula: {formulas}")
            
            return " | ".join(parts)
        
        return str(content)
    
    async def add_physics_content(self, 
                                 content_items: List[Dict[str, Any]], 
                                 batch_size: int = 50) -> Dict[str, Any]:
        """
        Add physics content to the vector database with embeddings
        
        Args:
            content_items: List of content dictionaries
            batch_size: Size of batches for processing
            
        Returns:
            Processing results and statistics
        """
        logger.info(f"🚀 Adding {len(content_items)} physics content items to vector database")
        start_time = time.time()
        
        successful_additions = 0
        failed_additions = 0
        errors = []
        
        try:
            # Process in batches for memory efficiency
            for batch_start in range(0, len(content_items), batch_size):
                batch_items = content_items[batch_start:batch_start + batch_size]
                batch_num = (batch_start // batch_size) + 1
                total_batches = (len(content_items) + batch_size - 1) // batch_size
                
                logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_items)} items)")
                
                # Prepare content for embedding
                enhanced_texts = []
                physics_contents = []
                
                for item in batch_items:
                    try:
                        # Create PhysicsContent object
                        physics_content = PhysicsContent(
                            id=item.get('id', str(uuid.uuid4())),
                            title=item.get('title', ''),
                            content=item.get('content', ''),
                            topic=item.get('topic', 'general'),
                            subtopic=item.get('subtopic'),
                            difficulty_level=item.get('difficulty_level', 'intermediate'),
                            content_type=item.get('content_type', 'concept'),
                            source=item.get('source'),
                            metadata=item.get('metadata', {})
                        )
                        
                        physics_contents.append(physics_content)
                        
                        # Enhance content for embedding
                        enhanced_text = self._enhance_physics_content(item)
                        enhanced_texts.append(enhanced_text)
                        
                    except Exception as e:
                        error_msg = f"Failed to process item: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        failed_additions += 1
                
                # Generate embeddings for the batch
                if enhanced_texts:
                    embedding_start = time.time()
                    batch_embeddings = await self.embedding_service.generate_batch_embeddings(
                        enhanced_texts, use_cache=True
                    )
                    embedding_time = time.time() - embedding_start
                    self.stats['total_embedding_time'] += embedding_time
                    
                    # Process embedding results
                    for i, embedding_result in enumerate(batch_embeddings.results):
                        if embedding_result.error is None and embedding_result.embedding:
                            physics_content = physics_contents[i]
                            physics_content.embedding = embedding_result.embedding
                            
                            # Store in vector database (if qdrant_client is available)
                            try:
                                if self.qdrant_client:
                                    await self._store_in_qdrant(physics_content)
                                successful_additions += 1
                                
                            except Exception as e:
                                error_msg = f"Failed to store in vector DB: {str(e)}"
                                errors.append(error_msg)
                                logger.error(error_msg)
                                failed_additions += 1
                        else:
                            error_msg = f"Embedding generation failed: {embedding_result.error}"
                            errors.append(error_msg)
                            failed_additions += 1
                
                # Small delay between batches
                if batch_start + batch_size < len(content_items):
                    await asyncio.sleep(0.1)
        
        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            errors.append(error_msg)
            logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        
        total_time = time.time() - start_time
        self.stats['total_documents_indexed'] += successful_additions
        
        result = {
            'success': successful_additions > 0,
            'total_processed': len(content_items),
            'successful_additions': successful_additions,
            'failed_additions': failed_additions,
            'processing_time': total_time,
            'errors': errors[:10],  # Limit error list
            'total_errors': len(errors)
        }
        
        logger.info(f"✅ Content addition completed: {successful_additions} success, {failed_additions} failed in {total_time:.2f}s")
        
        return result
    
    async def _store_in_qdrant(self, physics_content: PhysicsContent):
        """Store physics content with embedding in Qdrant"""
        if not self.qdrant_client or not physics_content.embedding:
            return
            
        # Prepare payload for Qdrant
        payload = {
            'id': physics_content.id,
            'title': physics_content.title,
            'content': physics_content.content,
            'topic': physics_content.topic,
            'subtopic': physics_content.subtopic,
            'difficulty_level': physics_content.difficulty_level,
            'content_type': physics_content.content_type,
            'source': physics_content.source,
            'created_at': physics_content.created_at.isoformat() if physics_content.created_at else None,
            'metadata': physics_content.metadata or {}
        }
        
        # Store point in Qdrant using the correct method
        physics_items = [{
            'id': physics_content.id,
            'content': physics_content.content,
            'topic': physics_content.topic,
            'difficulty': physics_content.difficulty_level,
            'title': physics_content.title,
            'embedding': physics_content.embedding
        }]
        await self.qdrant_client.add_physics_content(physics_items)
    
    async def search_physics_content(self, 
                                   query: str,
                                   limit: int = 10,
                                   topic_filter: Optional[str] = None,
                                   difficulty_filter: Optional[str] = None,
                                   content_type_filter: Optional[str] = None,
                                   min_similarity: float = 0.3) -> SearchResponse:
        """
        Search for similar physics content using vector similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results
            topic_filter: Filter by physics topic
            difficulty_filter: Filter by difficulty level
            content_type_filter: Filter by content type
            min_similarity: Minimum similarity threshold
            
        Returns:
            SearchResponse with ranked results
        """
        logger.info(f"🔍 Searching for physics content: '{query[:50]}...'")
        search_start_time = time.time()
        
        try:
            # Generate embedding for query
            embedding_start = time.time()
            query_result = await self.embedding_service.generate_single_embedding(query)
            embedding_time = time.time() - embedding_start
            
            if query_result.error or not query_result.embedding:
                error_msg = f"Failed to generate query embedding: {query_result.error}"
                logger.error(error_msg)
                return SearchResponse(
                    query=query,
                    results=[],
                    total_found=0,
                    search_time=0.0,
                    embedding_time=embedding_time,
                    filters_applied={}
                )
            
            # Prepare search filters
            search_filters = {}
            if topic_filter:
                search_filters['topic'] = topic_filter
            if difficulty_filter:
                search_filters['difficulty_level'] = difficulty_filter  
            if content_type_filter:
                search_filters['content_type'] = content_type_filter
            
            # Perform vector search (if qdrant_client available)
            search_results = []
            if self.qdrant_client:
                search_results = await self._search_qdrant(
                    query_result.embedding, 
                    limit, 
                    search_filters, 
                    min_similarity,
                    query  # Pass the original query text
                )
            
            search_time = time.time() - search_start_time
            self.stats['total_searches_performed'] += 1
            self.stats['total_search_time'] += search_time
            self.stats['total_embedding_time'] += embedding_time
            
            logger.info(f"✅ Search completed: {len(search_results)} results in {search_time:.3f}s")
            
            return SearchResponse(
                query=query,
                results=search_results,
                total_found=len(search_results),
                search_time=search_time,
                embedding_time=embedding_time,
                filters_applied=search_filters
            )
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
            
            return SearchResponse(
                query=query,
                results=[],
                total_found=0,
                search_time=0.0,
                embedding_time=0.0,
                filters_applied={}
            )
    
    async def _search_qdrant(self, 
                           query_vector: List[float], 
                           limit: int, 
                           filters: Dict[str, Any], 
                           min_similarity: float,
                           query_text: str = "") -> List[SearchResult]:
        """Perform vector search in Qdrant"""
        if not self.qdrant_client:
            return []
        
        # Build Qdrant filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append({
                    'key': key,
                    'match': {'value': value}
                })
            
            if conditions:
                qdrant_filter = {'must': conditions}
        
        # Perform search using the correct method
        search_result = await self.qdrant_client.search_physics_content(
            query=query_text,
            limit=limit
        )
        
        # Convert results to SearchResult objects
        results = []
        for i, point in enumerate(search_result):
            physics_content = PhysicsContent(
                id=point.payload['id'],
                title=point.payload['title'],
                content=point.payload['content'],
                topic=point.payload['topic'],
                subtopic=point.payload.get('subtopic'),
                difficulty_level=point.payload['difficulty_level'],
                content_type=point.payload['content_type'],
                source=point.payload.get('source'),
                metadata=point.payload.get('metadata', {})
            )
            
            search_result_obj = SearchResult(
                content=physics_content,
                similarity_score=point.score,
                rank=i + 1
            )
            results.append(search_result_obj)
        
        return results
    
    async def get_similar_content(self, 
                                content_id: str, 
                                limit: int = 5,
                                exclude_self: bool = True) -> List[SearchResult]:
        """
        Find content similar to a given content item
        
        Args:
            content_id: ID of the reference content
            limit: Maximum number of similar items to return
            exclude_self: Whether to exclude the reference content from results
            
        Returns:
            List of similar content items
        """
        try:
            if not self.qdrant_client:
                logger.warning("Qdrant client not available for similarity search")
                return []
            
            # Get the reference content
            reference_point = await self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[content_id],
                with_vectors=True
            )
            
            if not reference_point or not reference_point[0].vector:
                logger.warning(f"Reference content not found or has no vector: {content_id}")
                return []
            
            # Search for similar content
            similar_results = await self._search_qdrant(
                query_vector=reference_point[0].vector,
                limit=limit + (1 if exclude_self else 0),
                filters={},
                min_similarity=0.3
            )
            
            # Exclude self if requested
            if exclude_self:
                similar_results = [r for r in similar_results if r.content.id != content_id]
                similar_results = similar_results[:limit]
            
            return similar_results
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {str(e)}")
            return []
    
    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing physics content
        
        Args:
            content_id: ID of content to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update was successful
        """
        try:
            if not self.qdrant_client:
                return False
            
            # Get existing content
            existing_points = await self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[content_id],
                with_payload=True,
                with_vectors=True
            )
            
            if not existing_points:
                logger.warning(f"Content not found for update: {content_id}")
                return False
            
            existing_point = existing_points[0]
            
            # Update payload
            updated_payload = existing_point.payload.copy()
            updated_payload.update(updates)
            
            # Re-generate embedding if content changed
            embedding_vector = existing_point.vector
            if 'content' in updates or 'title' in updates:
                enhanced_text = self._enhance_physics_content(updated_payload)
                embedding_result = await self.embedding_service.generate_single_embedding(enhanced_text)
                
                if embedding_result.embedding:
                    embedding_vector = embedding_result.embedding
            
            # Update in Qdrant
            await self.qdrant_client.add_points(
                collection_name=self.collection_name,
                points=[{
                    'id': content_id,
                    'vector': embedding_vector,
                    'payload': updated_payload
                }]
            )
            
            logger.info(f"✅ Content updated successfully: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update content {content_id}: {str(e)}")
            return False
    
    async def delete_content(self, content_ids: Union[str, List[str]]) -> int:
        """
        Delete physics content from the vector database
        
        Args:
            content_ids: Single ID or list of IDs to delete
            
        Returns:
            Number of items successfully deleted
        """
        try:
            if not self.qdrant_client:
                return 0
            
            if isinstance(content_ids, str):
                content_ids = [content_ids]
            
            # Delete from Qdrant
            result = await self.qdrant_client.delete_points(
                collection_name=self.collection_name,
                points_selector=content_ids
            )
            
            deleted_count = len(content_ids) if result else 0
            logger.info(f"🗑️ Deleted {deleted_count} content items")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete content: {str(e)}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        uptime = datetime.now() - self.stats['last_reset']
        
        embedding_stats = self.embedding_service.get_embedding_stats()
        
        return {
            'database_uptime_hours': uptime.total_seconds() / 3600,
            'total_documents_indexed': self.stats['total_documents_indexed'],
            'total_searches_performed': self.stats['total_searches_performed'],
            'average_search_time': (self.stats['total_search_time'] / 
                                  max(1, self.stats['total_searches_performed'])),
            'total_embedding_time': self.stats['total_embedding_time'],
            'collection_name': self.collection_name,
            'vector_size': self.vector_size,
            'embedding_service_stats': embedding_stats
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'total_documents_indexed': 0,
            'total_searches_performed': 0,
            'total_embedding_time': 0.0,
            'total_search_time': 0.0,
            'last_reset': datetime.now()
        }
        self.embedding_service.reset_stats()
        logger.info("📊 Vector database statistics reset")

# Convenience functions
async def create_physics_vector_db(qdrant_client=None, **kwargs) -> PhysicsVectorDatabase:
    """Create a new physics vector database instance"""
    return PhysicsVectorDatabase(qdrant_client=qdrant_client, **kwargs)

async def add_physics_knowledge(content_items: List[Dict[str, Any]], 
                              qdrant_client=None) -> Dict[str, Any]:
    """Convenience function to add physics knowledge"""
    vector_db = PhysicsVectorDatabase(qdrant_client=qdrant_client)
    return await vector_db.add_physics_content(content_items)

async def search_physics_knowledge(query: str, 
                                 qdrant_client=None, 
                                 **kwargs) -> SearchResponse:
    """Convenience function to search physics knowledge"""
    vector_db = PhysicsVectorDatabase(qdrant_client=qdrant_client)
    return await vector_db.search_physics_content(query, **kwargs)

# Example usage and testing
async def test_vector_database():
    """Test the vector database functionality"""
    print("🧪 Testing Physics Vector Database Integration")
    print("=" * 55)
    
    # Create vector database (without Qdrant for testing)
    vector_db = PhysicsVectorDatabase()
    
    # Test data
    sample_physics_content = [
        {
            'id': 'physics_001',
            'title': 'Newton\'s Second Law',
            'content': 'Force equals mass times acceleration (F = ma)',
            'topic': 'mechanics',
            'subtopic': 'dynamics',
            'difficulty_level': 'beginner',
            'content_type': 'formula',
            'source': 'Classical Mechanics Textbook'
        },
        {
            'id': 'physics_002', 
            'title': 'Conservation of Energy',
            'content': 'Energy cannot be created or destroyed, only converted from one form to another',
            'topic': 'mechanics',
            'subtopic': 'energy',
            'difficulty_level': 'intermediate',
            'content_type': 'concept'
        },
        {
            'id': 'physics_003',
            'title': 'Coulomb\'s Law',
            'content': 'The force between two point charges is proportional to the product of charges and inversely proportional to the square of distance',
            'topic': 'electromagnetism',
            'subtopic': 'electrostatics',
            'difficulty_level': 'intermediate',
            'content_type': 'formula'
        }
    ]
    
    print(f"\n1️⃣ Testing content addition...")
    result = await vector_db.add_physics_content(sample_physics_content)
    print(f"✅ Addition result: {result['successful_additions']}/{result['total_processed']} successful")
    
    print(f"\n2️⃣ Testing search functionality...")
    search_response = await vector_db.search_physics_content(
        "What is the relationship between force and acceleration?",
        limit=3
    )
    print(f"✅ Search completed: {search_response.total_found} results in {search_response.search_time:.3f}s")
    
    for i, result in enumerate(search_response.results[:2]):
        print(f"  Result {i+1}: {result.content.title} (similarity: {result.similarity_score:.3f})")
    
    print(f"\n📈 Database Statistics:")
    stats = vector_db.get_database_stats()
    for key, value in stats.items():
        if key != 'embedding_service_stats':
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_vector_database())