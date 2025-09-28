"""
Performance Optimization Utilities
Provides caching, compression, database indexing, and other performance enhancements
"""

import functools
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, Union, List
from flask import request, g, current_app
import gzip
import io
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Simple in-memory cache with TTL support
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
        self.access_counts = {}
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Cleanup every 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        now = time.time()
        
        # Periodic cleanup
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
            self.last_cleanup = now
        
        if key in self.cache:
            value, expiry = self.cache[key]
            
            if now < expiry:
                # Track access for LRU-style eviction
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                # Expired
                del self.cache[key]
                if key in self.access_counts:
                    del self.access_counts[key]
                logger.debug(f"Cache expired: {key}")
        
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
        self.access_counts[key] = 1
        
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        
        # Prevent memory overflow - remove least accessed items if cache is too large
        if len(self.cache) > 1000:
            self._evict_lru_items(100)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_counts:
                del self.access_counts[key]
            logger.debug(f"Cache delete: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.access_counts.clear()
        logger.info("Cache cleared")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, (value, expiry) in self.cache.items()
            if now >= expiry
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_counts:
                del self.access_counts[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_lru_items(self, count: int) -> None:
        """Evict least recently used items"""
        if not self.access_counts:
            return
        
        # Sort by access count (ascending) and remove least accessed
        sorted_items = sorted(self.access_counts.items(), key=lambda x: x[1])
        
        for key, _ in sorted_items[:count]:
            if key in self.cache:
                del self.cache[key]
            del self.access_counts[key]
        
        logger.debug(f"Evicted {count} LRU cache entries")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        active_entries = sum(1 for _, expiry in self.cache.values() if now < expiry)
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': len(self.cache) - active_entries,
            'total_access_counts': sum(self.access_counts.values()),
            'average_access_count': (
                sum(self.access_counts.values()) / len(self.access_counts)
                if self.access_counts else 0
            )
        }


# Global cache instance
app_cache = InMemoryCache(default_ttl=300)  # 5 minutes


def cache_result(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_func: Optional function to generate cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = app_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Only cache if execution took significant time (avoid caching trivial operations)
            if execution_time > 0.01:  # 10ms threshold
                app_cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {func.__name__} (execution: {execution_time:.3f}s)")
            
            return result
        
        return wrapper
    return decorator


def cache_database_query(ttl: int = 300):
    """
    Decorator specifically for caching database query results
    """
    def generate_db_cache_key(*args, **kwargs):
        # Include user context in cache key for security
        user_id = getattr(g, 'user_id', 'anonymous')
        key_parts = [user_id]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"db_query:{hashlib.md5('|'.join(key_parts).encode()).hexdigest()}"
    
    return cache_result(ttl=ttl, key_func=generate_db_cache_key)


class ResponseCompressor:
    """
    Handle response compression to reduce bandwidth
    """
    
    @staticmethod
    def should_compress(response) -> bool:
        """Check if response should be compressed"""
        # Check content type
        if not response.content_type:
            return False
        
        compressible_types = [
            'application/json',
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'text/plain',
            'application/xml',
            'text/xml'
        ]
        
        for content_type in compressible_types:
            if response.content_type.startswith(content_type):
                break
        else:
            return False
        
        # Check if client supports gzip
        if 'gzip' not in request.headers.get('Accept-Encoding', ''):
            return False
        
        # Check response size (don't compress small responses)
        if response.content_length and response.content_length < 1024:  # 1KB
            return False
        
        # Check if already compressed
        if response.headers.get('Content-Encoding'):
            return False
        
        return True
    
    @staticmethod
    def compress_response(response):
        """Compress response data"""
        if not ResponseCompressor.should_compress(response):
            return response
        
        try:
            # Compress the data
            buffer = io.BytesIO()
            
            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz_file:
                if isinstance(response.data, str):
                    gz_file.write(response.data.encode('utf-8'))
                else:
                    gz_file.write(response.data)
            
            compressed_data = buffer.getvalue()
            
            # Update response
            response.data = compressed_data
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(compressed_data)
            
            # Calculate compression ratio
            original_size = len(response.get_data())
            compressed_size = len(compressed_data)
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.debug(f"Response compressed: {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)")
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
        
        return response


class DatabaseOptimizer:
    """
    Database performance optimization utilities
    """
    
    def __init__(self, db):
        self.db = db
    
    def create_indexes(self) -> List[str]:
        """
        Create optimized indexes for better query performance
        """
        created_indexes = []
        
        try:
            # Users collection indexes
            users_indexes = [
                IndexModel([("clerk_user_id", ASCENDING)], unique=True),
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("usage_analytics.last_activity", DESCENDING)])
            ]
            
            result = self.db.users.create_indexes(users_indexes)
            created_indexes.extend([f"users.{idx}" for idx in result])
            
            # MLModels collection indexes
            models_indexes = [
                IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
                IndexModel([("model_name", TEXT)]),  # Text search
                IndexModel([("model_type", ASCENDING)]),
                IndexModel([("is_public", ASCENDING), ("created_at", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("model_type", ASCENDING)]),
                IndexModel([("performance_metrics.accuracy", DESCENDING)]),
                IndexModel([("tags", ASCENDING)])
            ]
            
            result = self.db.mlmodels.create_indexes(models_indexes)
            created_indexes.extend([f"mlmodels.{idx}" for idx in result])
            
            # Simulations collection indexes
            simulations_indexes = [
                IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
                IndexModel([("simulation_name", TEXT)]),  # Text search
                IndexModel([("simulation_type", ASCENDING)]),
                IndexModel([("is_public", ASCENDING), ("created_at", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("simulation_type", ASCENDING)])
            ]
            
            result = self.db.simulations.create_indexes(simulations_indexes)
            created_indexes.extend([f"simulations.{idx}" for idx in result])
            
            logger.info(f"Created {len(created_indexes)} database indexes")
            
        except OperationFailure as e:
            logger.error(f"Failed to create some indexes: {str(e)}")
        
        return created_indexes
    
    def analyze_query_performance(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query performance and suggest optimizations
        """
        try:
            collection = getattr(self.db, collection_name)
            
            # Explain the query
            explain_result = collection.find(query).explain()
            
            analysis = {
                'execution_time_ms': explain_result.get('executionTimeMillis', 0),
                'documents_examined': explain_result.get('totalDocsExamined', 0),
                'documents_returned': explain_result.get('totalDocsReturned', 0),
                'index_used': explain_result.get('indexUsed', False),
                'winning_plan': explain_result.get('queryPlanner', {}).get('winningPlan', {})
            }
            
            # Performance suggestions
            suggestions = []
            
            if analysis['documents_examined'] > analysis['documents_returned'] * 10:
                suggestions.append("Consider adding an index for better selectivity")
            
            if analysis['execution_time_ms'] > 100:
                suggestions.append("Query is slow, consider optimizing indexes or query structure")
            
            if not analysis['index_used']:
                suggestions.append("Query is not using any index, consider adding appropriate indexes")
            
            analysis['suggestions'] = suggestions
            
            return analysis
            
        except Exception as e:
            logger.error(f"Query analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get database collection statistics"""
        stats = {}
        
        for collection_name in ['users', 'mlmodels', 'simulations']:
            try:
                collection_stats = self.db.command("collStats", collection_name)
                
                stats[collection_name] = {
                    'count': collection_stats.get('count', 0),
                    'size': collection_stats.get('size', 0),
                    'avgObjSize': collection_stats.get('avgObjSize', 0),
                    'storageSize': collection_stats.get('storageSize', 0),
                    'indexes': collection_stats.get('nindexes', 0),
                    'indexSize': collection_stats.get('totalIndexSize', 0)
                }
                
            except Exception as e:
                logger.error(f"Failed to get stats for {collection_name}: {str(e)}")
                stats[collection_name] = {'error': str(e)}
        
        return stats


class PerformanceMonitor:
    """
    Monitor and track performance metrics
    """
    
    def __init__(self):
        self.request_times = []
        self.slow_queries = []
        self.error_rates = {}
    
    def start_request(self):
        """Mark start of request processing"""
        g.start_time = time.time()
    
    def end_request(self, response):
        """Mark end of request processing and record metrics"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Record request time
            self.request_times.append({
                'endpoint': request.endpoint,
                'method': request.method,
                'duration': duration,
                'timestamp': datetime.now(),
                'status_code': response.status_code
            })
            
            # Keep only recent requests (last 1000)
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
            
            # Log slow requests
            if duration > 2.0:  # 2 second threshold
                logger.warning(
                    f"Slow request: {request.method} {request.path} - {duration:.3f}s"
                )
                
                self.slow_queries.append({
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'timestamp': datetime.now()
                })
                
                # Keep only recent slow queries
                if len(self.slow_queries) > 100:
                    self.slow_queries = self.slow_queries[-100:]
        
        return response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.request_times:
            return {'message': 'No performance data available'}
        
        # Calculate statistics
        durations = [req['duration'] for req in self.request_times]
        
        stats = {
            'total_requests': len(self.request_times),
            'avg_response_time': sum(durations) / len(durations),
            'min_response_time': min(durations),
            'max_response_time': max(durations),
            'slow_requests': len(self.slow_queries),
            'requests_per_endpoint': {},
            'avg_time_per_endpoint': {}
        }
        
        # Per-endpoint statistics
        endpoint_times = {}
        for req in self.request_times:
            endpoint = req['endpoint'] or 'unknown'
            if endpoint not in endpoint_times:
                endpoint_times[endpoint] = []
            endpoint_times[endpoint].append(req['duration'])
        
        for endpoint, times in endpoint_times.items():
            stats['requests_per_endpoint'][endpoint] = len(times)
            stats['avg_time_per_endpoint'][endpoint] = sum(times) / len(times)
        
        # Recent slow queries
        stats['recent_slow_queries'] = [
            {
                'endpoint': query['endpoint'],
                'method': query['method'],
                'duration': query['duration'],
                'timestamp': query['timestamp'].isoformat()
            }
            for query in self.slow_queries[-10:]  # Last 10 slow queries
        ]
        
        return stats


# Global performance monitor
performance_monitor = PerformanceMonitor()


def setup_performance_monitoring(app):
    """Setup performance monitoring for Flask app"""
    
    @app.before_request
    def before_request():
        performance_monitor.start_request()
    
    @app.after_request
    def after_request(response):
        # Apply compression
        response = ResponseCompressor.compress_response(response)
        
        # Record performance metrics
        performance_monitor.end_request(response)
        
        return response


def optimize_database_performance(db):
    """
    Run database performance optimization
    """
    optimizer = DatabaseOptimizer(db)
    
    # Create indexes
    created_indexes = optimizer.create_indexes()
    
    # Get collection stats
    stats = optimizer.get_collection_stats()
    
    logger.info(f"Database optimization complete. Created {len(created_indexes)} indexes.")
    
    return {
        'indexes_created': created_indexes,
        'collection_stats': stats
    }


# Utility functions for common caching patterns
def cache_user_data(user_id: str, data: Any, ttl: int = 300):
    """Cache user-specific data"""
    cache_key = f"user_data:{user_id}"
    app_cache.set(cache_key, data, ttl)


def get_cached_user_data(user_id: str) -> Optional[Any]:
    """Get cached user-specific data"""
    cache_key = f"user_data:{user_id}"
    return app_cache.get(cache_key)


def invalidate_user_cache(user_id: str):
    """Invalidate all cached data for a user"""
    # Note: This is a simple implementation
    # In production, you might want a more sophisticated cache tagging system
    cache_key = f"user_data:{user_id}"
    app_cache.delete(cache_key)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return app_cache.stats()


def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics"""
    return performance_monitor.get_performance_stats()