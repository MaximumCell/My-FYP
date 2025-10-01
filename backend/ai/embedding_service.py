"""
Advanced Physics AI Embedding Service
====================================

This module provides comprehensive embedding functionality for physics content
using Google's text-embedding-004 model. It includes batch processing,
caching, error handling, and integration with the Qdrant vector database.

Features:
- Google text-embedding-004 integration
- Batch processing for efficiency
- Intelligent caching system
- Comprehensive error handling
- Physics content optimization
- Vector similarity search
- Performance monitoring

Author: Physics AI Tutor Team
Date: September 28, 2025
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import os

import google.generativeai as genai
import numpy as np
from dataclasses import dataclass
from functools import wraps
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result container for embedding operations"""
    text: str
    embedding: List[float]
    model: str
    timestamp: datetime
    processing_time: float
    error: Optional[str] = None

@dataclass
class BatchEmbeddingResult:
    """Result container for batch embedding operations"""
    results: List[EmbeddingResult]
    total_processed: int
    total_time: float
    errors: List[str]
    cache_hits: int = 0
    api_calls: int = 0

class EmbeddingCache:
    """Intelligent caching system for embeddings"""
    
    def __init__(self, max_size: int = 10000, ttl_hours: int = 24):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        
    def _get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model"""
        content = f"{text}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, model: str) -> Optional[List[float]]:
        """Get embedding from cache if available and not expired"""
        key = self._get_cache_key(text, model)
        
        if key not in self.cache:
            return None
            
        entry_time, embedding = self.cache[key]
        if datetime.now() - entry_time > self.ttl:
            # Entry expired
            self._remove_entry(key)
            return None
            
        # Update access time for LRU
        self.access_times[key] = datetime.now()
        return embedding
    
    def put(self, text: str, model: str, embedding: List[float]) -> None:
        """Store embedding in cache with LRU eviction"""
        key = self._get_cache_key(text, model)
        
        # Clean cache if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()
            
        self.cache[key] = (datetime.now(), embedding)
        self.access_times[key] = datetime.now()
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and access times"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries"""
        if not self.access_times:
            return
            
        # Remove 20% of entries (LRU)
        num_to_remove = max(1, len(self.access_times) // 5)
        sorted_entries = sorted(self.access_times.items(), key=lambda x: x[1])
        
        for key, _ in sorted_entries[:num_to_remove]:
            self._remove_entry(key)
    
    def clear(self) -> None:
        """Clear all cached embeddings"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_count = 0
        
        current_time = datetime.now()
        for entry_time, _ in self.cache.values():
            if current_time - entry_time > self.ttl:
                expired_count += 1
                
        return {
            'total_entries': total_entries,
            'max_size': self.max_size,
            'expired_entries': expired_count,
            'cache_utilization': total_entries / self.max_size if self.max_size > 0 else 0,
            'ttl_hours': self.ttl.total_seconds() / 3600
        }

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
                        
            raise last_exception
        return wrapper
    return decorator

class PhysicsEmbeddingService:
    """
    Advanced embedding service for physics content using Google's text-embedding-004
    
    This service provides:
    - High-quality embeddings optimized for physics content
    - Batch processing for efficiency
    - Intelligent caching to reduce API calls
    - Comprehensive error handling and retry logic
    - Performance monitoring and analytics
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: str = "text-embedding-004",
                 cache_size: int = 10000,
                 cache_ttl_hours: int = 24,
                 max_batch_size: int = 100,
                 rate_limit_delay: float = 0.1):
        """
        Initialize the embedding service
        
        Args:
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
            model_name: Embedding model to use
            cache_size: Maximum number of cached embeddings
            cache_ttl_hours: Cache time-to-live in hours
            max_batch_size: Maximum batch size for processing
            rate_limit_delay: Delay between API calls to respect rate limits
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = model_name
        self.max_batch_size = max_batch_size
        self.rate_limit_delay = rate_limit_delay
        
        # Initialize components
        self.cache = EmbeddingCache(cache_size, cache_ttl_hours)
        self.stats = {
            'total_embeddings_generated': 0,
            'total_api_calls': 0,
            'total_cache_hits': 0,
            'total_processing_time': 0.0,
            'error_count': 0,
            'last_reset': datetime.now()
        }
        
        # Configure Google Generative AI
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GEMINI_API_KEY environment variable.")
            
        try:
            genai.configure(api_key=self.api_key)
            logger.info(f"✅ Embedding service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Generative AI: {e}")
            raise
    
    def preprocess_physics_text(self, text: str) -> str:
        """
        Preprocess text for better physics embedding quality
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text optimized for physics embeddings
        """
        if not text or not text.strip():
            return ""
            
        # Clean and normalize text
        processed_text = text.strip()
        
        # Add physics context prefix to improve embedding quality
        physics_keywords = ['force', 'energy', 'momentum', 'velocity', 'acceleration', 
                          'mass', 'charge', 'field', 'wave', 'particle', 'quantum',
                          'equation', 'formula', 'law', 'principle', 'theorem']
        
        has_physics_content = any(keyword in processed_text.lower() for keyword in physics_keywords)
        
        if has_physics_content and not processed_text.lower().startswith('physics'):
            processed_text = f"Physics concept: {processed_text}"
            
        return processed_text
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def generate_single_embedding(self, text: str, use_cache: bool = True) -> EmbeddingResult:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            use_cache: Whether to use caching
            
        Returns:
            EmbeddingResult containing the embedding and metadata
        """
        start_time = time.time()
        
        try:
            # Preprocess text
            processed_text = self.preprocess_physics_text(text)
            
            if not processed_text:
                return EmbeddingResult(
                    text=text,
                    embedding=[],
                    model=self.model_name,
                    timestamp=datetime.now(),
                    processing_time=0.0,
                    error="Empty text after preprocessing"
                )
            
            # Check cache first
            if use_cache:
                cached_embedding = self.cache.get(processed_text, self.model_name)
                if cached_embedding is not None:
                    self.stats['total_cache_hits'] += 1
                    return EmbeddingResult(
                        text=text,
                        embedding=cached_embedding,
                        model=self.model_name,
                        timestamp=datetime.now(),
                        processing_time=time.time() - start_time
                    )
            
            # Generate embedding using Google's API
            try:
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
                # Create embedding request
                response = genai.embed_content(
                    model=f"models/{self.model_name}",
                    content=processed_text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                
                embedding = response['embedding']
                
                # Update statistics
                self.stats['total_api_calls'] += 1
                self.stats['total_embeddings_generated'] += 1
                
                # Cache the result
                if use_cache:
                    self.cache.put(processed_text, self.model_name, embedding)
                
                processing_time = time.time() - start_time
                self.stats['total_processing_time'] += processing_time
                
                return EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    model=self.model_name,
                    timestamp=datetime.now(),
                    processing_time=processing_time
                )
                
            except Exception as api_error:
                logger.error(f"API call failed for text '{text[:50]}...': {api_error}")
                self.stats['error_count'] += 1
                raise
                
        except Exception as e:
            error_msg = f"Failed to generate embedding: {str(e)}"
            logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
            self.stats['error_count'] += 1
            
            return EmbeddingResult(
                text=text,
                embedding=[],
                model=self.model_name,
                timestamp=datetime.now(),
                processing_time=time.time() - start_time,
                error=error_msg
            )
    
    async def generate_batch_embeddings(self, 
                                      texts: List[str], 
                                      use_cache: bool = True,
                                      progress_callback: Optional[callable] = None) -> BatchEmbeddingResult:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use caching
            progress_callback: Optional callback for progress updates
            
        Returns:
            BatchEmbeddingResult containing all results and statistics
        """
        start_time = time.time()
        results = []
        errors = []
        cache_hits = 0
        api_calls = 0
        
        logger.info(f"🚀 Starting batch embedding generation for {len(texts)} texts")
        
        # Process texts in batches to respect rate limits
        for i in range(0, len(texts), self.max_batch_size):
            batch_texts = texts[i:i + self.max_batch_size]
            batch_number = (i // self.max_batch_size) + 1
            total_batches = (len(texts) + self.max_batch_size - 1) // self.max_batch_size
            
            logger.info(f"📦 Processing batch {batch_number}/{total_batches} ({len(batch_texts)} texts)")
            
            # Process batch concurrently but with rate limiting
            batch_tasks = [
                self.generate_single_embedding(text, use_cache) 
                for text in batch_texts
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process batch results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    error_msg = f"Batch {batch_number}, item {j+1}: {str(result)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                elif isinstance(result, EmbeddingResult):
                    results.append(result)
                    if result.error is None and len(result.embedding) > 0:
                        # Check if this was a cache hit (very fast processing time)
                        if result.processing_time < 0.1:
                            cache_hits += 1
                        else:
                            api_calls += 1
                    elif result.error:
                        errors.append(result.error)
            
            # Progress callback
            if progress_callback:
                progress = min(i + len(batch_texts), len(texts))
                progress_callback(progress, len(texts), batch_number, total_batches)
                
            # Small delay between batches to respect rate limits
            if i + self.max_batch_size < len(texts):
                await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        logger.info(f"✅ Batch embedding completed in {total_time:.2f}s")
        logger.info(f"📊 Results: {len(results)} successful, {len(errors)} errors, {cache_hits} cache hits, {api_calls} API calls")
        
        return BatchEmbeddingResult(
            results=results,
            total_processed=len(results),
            total_time=total_time,
            errors=errors,
            cache_hits=cache_hits,
            api_calls=api_calls
        )
    
    async def embed_physics_content(self, content: Union[str, Dict[str, Any], List[str]]) -> Union[EmbeddingResult, BatchEmbeddingResult]:
        """
        Main method to embed physics content with automatic type detection
        
        Args:
            content: Text string, structured content dict, or list of texts
            
        Returns:
            Appropriate result type based on input
        """
        if isinstance(content, str):
            return await self.generate_single_embedding(content)
        elif isinstance(content, list):
            return await self.generate_batch_embeddings(content)
        elif isinstance(content, dict):
            # Handle structured physics content
            text_parts = []
            
            if 'title' in content:
                text_parts.append(f"Title: {content['title']}")
            if 'concept_explanation' in content:
                text_parts.append(f"Concept: {content['concept_explanation']}")
            if 'key_formulas' in content:
                formulas = ', '.join(content['key_formulas'])
                text_parts.append(f"Formulas: {formulas}")
            if 'topic' in content:
                text_parts.append(f"Topic: {content['topic']}")
                
            combined_text = ' | '.join(text_parts)
            return await self.generate_single_embedding(combined_text)
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        if not embedding1 or not embedding2:
            return 0.0
            
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_similar_embeddings(self, 
                               query_embedding: List[float], 
                               candidate_embeddings: List[Tuple[str, List[float]]], 
                               top_k: int = 5,
                               min_similarity: float = 0.3) -> List[Tuple[str, float]]:
        """
        Find most similar embeddings to a query
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of (text, embedding) tuples
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (text, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for text, embedding in candidate_embeddings:
            similarity = self.calculate_similarity(query_embedding, embedding)
            if similarity >= min_similarity:
                similarities.append((text, similarity))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get comprehensive embedding service statistics"""
        cache_stats = self.cache.get_stats()
        
        uptime = datetime.now() - self.stats['last_reset']
        
        return {
            'service_uptime_hours': uptime.total_seconds() / 3600,
            'total_embeddings_generated': self.stats['total_embeddings_generated'],
            'total_api_calls': self.stats['total_api_calls'],
            'total_cache_hits': self.stats['total_cache_hits'],
            'cache_hit_ratio': (self.stats['total_cache_hits'] / 
                              max(1, self.stats['total_cache_hits'] + self.stats['total_api_calls'])),
            'average_processing_time': (self.stats['total_processing_time'] / 
                                      max(1, self.stats['total_embeddings_generated'])),
            'error_rate': (self.stats['error_count'] / 
                          max(1, self.stats['total_embeddings_generated'])),
            'cache_statistics': cache_stats,
            'model_name': self.model_name,
            'max_batch_size': self.max_batch_size
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.stats = {
            'total_embeddings_generated': 0,
            'total_api_calls': 0,
            'total_cache_hits': 0,
            'total_processing_time': 0.0,
            'error_count': 0,
            'last_reset': datetime.now()
        }
        logger.info("📊 Embedding service statistics reset")
    
    def clear_cache(self) -> None:
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("🗑️ Embedding cache cleared")

# Global embedding service instance
_embedding_service: Optional[PhysicsEmbeddingService] = None

def get_embedding_service() -> PhysicsEmbeddingService:
    """Get or create the global embedding service instance"""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = PhysicsEmbeddingService()
        
    return _embedding_service

def create_embedding_service(**kwargs) -> PhysicsEmbeddingService:
    """Create a new embedding service with custom configuration"""
    return PhysicsEmbeddingService(**kwargs)

# Convenience functions
async def embed_text(text: str, use_cache: bool = True) -> EmbeddingResult:
    """Convenience function to embed a single text"""
    service = get_embedding_service()
    return await service.generate_single_embedding(text, use_cache)

async def embed_texts(texts: List[str], use_cache: bool = True) -> BatchEmbeddingResult:
    """Convenience function to embed multiple texts"""
    service = get_embedding_service()
    return await service.generate_batch_embeddings(texts, use_cache)

async def embed_physics_content(content: Union[str, Dict[str, Any], List[str]]) -> Union[EmbeddingResult, BatchEmbeddingResult]:
    """Convenience function to embed physics content"""
    service = get_embedding_service()
    return await service.embed_physics_content(content)

# Example usage and testing functions
async def test_embedding_service():
    """Test the embedding service functionality"""
    print("🧪 Testing Physics Embedding Service")
    print("=" * 50)
    
    service = get_embedding_service()
    
    # Test single embedding
    print("\n1️⃣ Testing single embedding generation...")
    result = await service.generate_single_embedding(
        "Newton's second law states that force equals mass times acceleration"
    )
    
    if result.error:
        print(f"❌ Error: {result.error}")
    else:
        print(f"✅ Generated embedding with {len(result.embedding)} dimensions")
        print(f"⏱️ Processing time: {result.processing_time:.3f}s")
    
    # Test batch embeddings
    print("\n2️⃣ Testing batch embedding generation...")
    physics_texts = [
        "Energy is conserved in isolated systems",
        "Momentum is the product of mass and velocity",
        "Electric field is force per unit charge",
        "Wave-particle duality in quantum mechanics",
        "Thermodynamic equilibrium and entropy"
    ]
    
    batch_result = await service.generate_batch_embeddings(physics_texts)
    print(f"✅ Processed {batch_result.total_processed} texts in {batch_result.total_time:.3f}s")
    print(f"📊 Cache hits: {batch_result.cache_hits}, API calls: {batch_result.api_calls}")
    
    if batch_result.errors:
        print(f"❌ Errors encountered: {len(batch_result.errors)}")
    
    # Test similarity calculation
    if len(batch_result.results) >= 2:
        print("\n3️⃣ Testing similarity calculation...")
        emb1 = batch_result.results[0].embedding
        emb2 = batch_result.results[1].embedding
        
        if emb1 and emb2:
            similarity = service.calculate_similarity(emb1, emb2)
            print(f"✅ Similarity between first two texts: {similarity:.3f}")
    
    # Show statistics
    print("\n📈 Service Statistics:")
    stats = service.get_embedding_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    # Run tests if this module is executed directly
    asyncio.run(test_embedding_service())