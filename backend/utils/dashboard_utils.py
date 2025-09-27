"""
Dashboard Utilities and Caching for PhysicsLab Application
Provides caching mechanisms and reusable data aggregation services
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from functools import wraps
from bson import ObjectId

logger = logging.getLogger(__name__)

class DashboardCache:
    """Simple in-memory cache for dashboard data"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        
    def _get_cache_key(self, clerk_user_id: str, cache_type: str, **kwargs) -> str:
        """Generate cache key"""
        key_parts = [clerk_user_id, cache_type]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return ":".join(key_parts)
    
    def get(self, clerk_user_id: str, cache_type: str, **kwargs) -> Optional[Any]:
        """Get data from cache"""
        try:
            cache_key = self._get_cache_key(clerk_user_id, cache_type, **kwargs)
            
            if cache_key not in self._cache:
                return None
            
            cache_entry = self._cache[cache_key]
            
            # Check if cache has expired
            if time.time() > cache_entry['expires_at']:
                del self._cache[cache_key]
                return None
            
            logger.debug(f"Cache hit for key: {cache_key}")
            return cache_entry['data']
            
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None
    
    def set(self, clerk_user_id: str, cache_type: str, data: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set data in cache"""
        try:
            cache_key = self._get_cache_key(clerk_user_id, cache_type, **kwargs)
            ttl = ttl or self.default_ttl
            
            self._cache[cache_key] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            
            logger.debug(f"Cache set for key: {cache_key}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def invalidate(self, clerk_user_id: str, cache_type: Optional[str] = None) -> int:
        """Invalidate cache entries for a user"""
        try:
            keys_to_remove = []
            
            for cache_key in self._cache.keys():
                if cache_key.startswith(clerk_user_id):
                    if cache_type is None or f":{cache_type}:" in cache_key:
                        keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._cache[key]
            
            logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for {clerk_user_id}")
            return len(keys_to_remove)
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return 0
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            keys_to_remove = []
            
            for cache_key, cache_entry in self._cache.items():
                if current_time > cache_entry['expires_at']:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._cache[key]
            
            logger.debug(f"Cleaned up {len(keys_to_remove)} expired cache entries")
            return len(keys_to_remove)
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            current_time = time.time()
            total_entries = len(self._cache)
            expired_entries = 0
            
            for cache_entry in self._cache.values():
                if current_time > cache_entry['expires_at']:
                    expired_entries += 1
            
            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries,
                "cache_hit_ratio": getattr(self, '_hit_ratio', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

# Global cache instance
dashboard_cache = DashboardCache()

def cached_dashboard_data(cache_type: str, ttl: int = 300):
    """Decorator for caching dashboard data"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Extract clerk_user_id from arguments
                clerk_user_id = None
                if 'clerk_user_id' in kwargs:
                    clerk_user_id = kwargs['clerk_user_id']
                elif len(args) > 0 and hasattr(args[0], 'clerk_user_id'):
                    clerk_user_id = args[0].clerk_user_id
                
                if not clerk_user_id:
                    # If we can't find user ID, execute without caching
                    return func(*args, **kwargs)
                
                # Try to get from cache
                cache_kwargs = {k: v for k, v in kwargs.items() if k != 'clerk_user_id'}
                cached_result = dashboard_cache.get(clerk_user_id, cache_type, **cache_kwargs)
                
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                dashboard_cache.set(clerk_user_id, cache_type, result, ttl, **cache_kwargs)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in caching decorator: {str(e)}")
                # Execute function without caching if there's an error
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

class DataAggregationService:
    """Service for common data aggregation operations"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_project_counts(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, int]:
        """Get project counts with optional date filtering"""
        try:
            query = {"user_id": ObjectId(user_id)}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                query["created_at"] = date_filter
            
            models_count = self.db.ml_models.count_documents(query)
            simulations_count = self.db.simulations.count_documents(query)
            
            return {
                "models_count": models_count,
                "simulations_count": simulations_count,
                "total_count": models_count + simulations_count
            }
            
        except Exception as e:
            logger.error(f"Error getting project counts: {str(e)}")
            return {"models_count": 0, "simulations_count": 0, "total_count": 0}
    
    def get_time_series_data(self, user_id: str, days: int = 30, granularity: str = "daily") -> Dict[str, List]:
        """Get time series data for charts"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Define date grouping based on granularity
            if granularity == "daily":
                date_format = "%Y-%m-%d"
            elif granularity == "weekly":
                date_format = "%Y-W%U"
            else:  # monthly
                date_format = "%Y-%m"
            
            group_format = {"$dateToString": {"format": date_format, "date": "$created_at"}}
            
            # Models timeline
            model_pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": group_format,
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            # Simulations timeline
            simulation_pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": group_format,
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            models_timeline = list(self.db.ml_models.aggregate(model_pipeline))
            simulations_timeline = list(self.db.simulations.aggregate(simulation_pipeline))
            
            return {
                "models_timeline": models_timeline,
                "simulations_timeline": simulations_timeline,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting time series data: {str(e)}")
            return {"models_timeline": [], "simulations_timeline": [], "date_range": {}}
    
    def get_storage_breakdown(self, user_id: str) -> Dict[str, Any]:
        """Get detailed storage usage breakdown"""
        try:
            # Model files storage
            model_storage_pipeline = [
                {
                    "$match": {"user_id": ObjectId(user_id)}
                },
                {
                    "$group": {
                        "_id": None,
                        "total_size": {"$sum": "$file_size"},
                        "count": {"$sum": 1},
                        "avg_size": {"$avg": "$file_size"}
                    }
                }
            ]
            
            # Simulation files storage
            simulation_storage_pipeline = [
                {
                    "$match": {"user_id": ObjectId(user_id)}
                },
                {
                    "$group": {
                        "_id": None,
                        "total_size": {"$sum": "$file_size"},
                        "count": {"$sum": 1},
                        "avg_size": {"$avg": "$file_size"}
                    }
                }
            ]
            
            model_storage = list(self.db.ml_models.aggregate(model_storage_pipeline))
            simulation_storage = list(self.db.simulations.aggregate(simulation_storage_pipeline))
            
            model_size = model_storage[0]["total_size"] if model_storage else 0
            simulation_size = simulation_storage[0]["total_size"] if simulation_storage else 0
            total_size = model_size + simulation_size
            
            def format_size(size_bytes):
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{round(size_bytes / 1024, 1)} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    return f"{round(size_bytes / (1024 * 1024), 1)} MB"
                else:
                    return f"{round(size_bytes / (1024 * 1024 * 1024), 2)} GB"
            
            return {
                "total_size": total_size,
                "total_size_formatted": format_size(total_size),
                "models": {
                    "size": model_size,
                    "size_formatted": format_size(model_size),
                    "count": model_storage[0]["count"] if model_storage else 0,
                    "avg_size": model_storage[0]["avg_size"] if model_storage else 0,
                    "percentage": round((model_size / total_size) * 100, 1) if total_size > 0 else 0
                },
                "simulations": {
                    "size": simulation_size,
                    "size_formatted": format_size(simulation_size),
                    "count": simulation_storage[0]["count"] if simulation_storage else 0,
                    "avg_size": simulation_storage[0]["avg_size"] if simulation_storage else 0,
                    "percentage": round((simulation_size / total_size) * 100, 1) if total_size > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting storage breakdown: {str(e)}")
            return {"total_size": 0, "total_size_formatted": "0 B", "models": {}, "simulations": {}}
    
    def get_performance_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance summary statistics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Model performance aggregation
            model_perf_pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_accuracy": {"$avg": "$performance_metrics.accuracy"},
                        "max_accuracy": {"$max": "$performance_metrics.accuracy"},
                        "min_accuracy": {"$min": "$performance_metrics.accuracy"},
                        "avg_training_time": {"$avg": "$training_time"},
                        "total_training_time": {"$sum": "$training_time"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            # Simulation performance aggregation
            sim_perf_pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_execution_time": {"$avg": "$execution_time"},
                        "max_execution_time": {"$max": "$execution_time"},
                        "min_execution_time": {"$min": "$execution_time"},
                        "total_execution_time": {"$sum": "$execution_time"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            model_perf = list(self.db.ml_models.aggregate(model_perf_pipeline))
            sim_perf = list(self.db.simulations.aggregate(sim_perf_pipeline))
            
            return {
                "period_days": days,
                "models": {
                    "count": model_perf[0]["count"] if model_perf else 0,
                    "avg_accuracy": round(model_perf[0]["avg_accuracy"] or 0, 3) if model_perf else 0,
                    "max_accuracy": round(model_perf[0]["max_accuracy"] or 0, 3) if model_perf else 0,
                    "min_accuracy": round(model_perf[0]["min_accuracy"] or 0, 3) if model_perf else 0,
                    "avg_training_time": round(model_perf[0]["avg_training_time"] or 0, 2) if model_perf else 0,
                    "total_training_time": round(model_perf[0]["total_training_time"] or 0, 2) if model_perf else 0
                },
                "simulations": {
                    "count": sim_perf[0]["count"] if sim_perf else 0,
                    "avg_execution_time": round(sim_perf[0]["avg_execution_time"] or 0, 2) if sim_perf else 0,
                    "max_execution_time": round(sim_perf[0]["max_execution_time"] or 0, 2) if sim_perf else 0,
                    "min_execution_time": round(sim_perf[0]["min_execution_time"] or 0, 2) if sim_perf else 0,
                    "total_execution_time": round(sim_perf[0]["total_execution_time"] or 0, 2) if sim_perf else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {"period_days": days, "models": {"count": 0}, "simulations": {"count": 0}}

def get_aggregation_service():
    """Get DataAggregationService instance"""
    try:
        from utils.database import get_database
        db = get_database()
        return DataAggregationService(db)
    except Exception as e:
        logger.error(f"Failed to get aggregation service: {str(e)}")
        return None

def invalidate_user_cache(clerk_user_id: str, cache_types: Optional[List[str]] = None):
    """Utility function to invalidate user cache"""
    try:
        if cache_types:
            total_invalidated = 0
            for cache_type in cache_types:
                total_invalidated += dashboard_cache.invalidate(clerk_user_id, cache_type)
        else:
            total_invalidated = dashboard_cache.invalidate(clerk_user_id)
        
        logger.info(f"Invalidated {total_invalidated} cache entries for user {clerk_user_id}")
        return total_invalidated
    except Exception as e:
        logger.error(f"Error invalidating user cache: {str(e)}")
        return 0

def cleanup_cache():
    """Utility function to clean up expired cache entries"""
    try:
        cleaned = dashboard_cache.cleanup_expired()
        logger.info(f"Cleaned up {cleaned} expired cache entries")
        return cleaned
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}")
        return 0

# Background task to periodically clean up cache
def schedule_cache_cleanup():
    """Schedule periodic cache cleanup (would be called by a scheduler)"""
    import threading
    import time
    
    def cleanup_worker():
        while True:
            time.sleep(600)  # Clean up every 10 minutes
            cleanup_cache()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logger.info("Started cache cleanup background task")