"""
Analytics Tracker for PhysicsLab Application
Handles automatic tracking of user activities and analytics updates
"""
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from functools import wraps
from flask import request, g

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Class to handle user activity tracking and analytics updates"""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
    
    def _invalidate_user_dashboard_cache(self, clerk_user_id: str):
        """Helper method to invalidate user dashboard cache"""
        try:
            # Import here to avoid circular imports
            from utils.dashboard_utils import invalidate_user_cache
            invalidate_user_cache(clerk_user_id, ['dashboard', 'analytics', 'trends'])
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {clerk_user_id}: {str(e)}")
        
    def track_model_training(self, clerk_user_id: str, training_time: float, model_data: Dict[str, Any]):
        """Track ML model training activity"""
        try:
            # Convert to rounded float for more accurate tracking
            training_time_rounded = round(float(training_time), 2)
            
            update_data = {
                "$inc": {
                    "usage_analytics.total_models_trained": 1,
                    "usage_analytics.total_training_time": training_time_rounded
                },
                "$set": {
                    "usage_analytics.last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = self.users_collection.update_one(
                {"clerk_user_id": clerk_user_id},
                update_data
            )
            
            # Invalidate dashboard cache for this user
            self._invalidate_user_dashboard_cache(clerk_user_id)
            
            logger.info(f"Tracked model training for user {clerk_user_id}: {training_time_rounded}s")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error tracking model training: {str(e)}")
            return False
    
    def track_simulation_run(self, clerk_user_id: str, execution_time: float, simulation_data: Dict[str, Any]):
        """Track simulation run activity"""
        try:
            update_data = {
                "$inc": {
                    "usage_analytics.total_simulations_run": 1
                },
                "$set": {
                    "usage_analytics.last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = self.users_collection.update_one(
                {"clerk_user_id": clerk_user_id},
                update_data
            )
            
            # Invalidate dashboard cache for this user
            self._invalidate_user_dashboard_cache(clerk_user_id)
            
            logger.info(f"Tracked simulation run for user {clerk_user_id}: {execution_time}s")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error tracking simulation run: {str(e)}")
            return False
    
    def track_user_session(self, clerk_user_id: str):
        """Track user session activity"""
        try:
            update_data = {
                "$set": {
                    "usage_analytics.last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = self.users_collection.update_one(
                {"clerk_user_id": clerk_user_id},
                update_data
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error tracking user session: {str(e)}")
            return False
    
    def track_file_upload(self, clerk_user_id: str, file_size: int, file_type: str):
        """Track file upload activity"""
        try:
            # Update last activity
            update_data = {
                "$set": {
                    "usage_analytics.last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = self.users_collection.update_one(
                {"clerk_user_id": clerk_user_id},
                update_data
            )
            
            logger.info(f"Tracked file upload for user {clerk_user_id}: {file_size} bytes ({file_type})")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error tracking file upload: {str(e)}")
            return False
    
    def track_api_usage(self, clerk_user_id: str, endpoint: str, method: str, status_code: int):
        """Track API endpoint usage"""
        try:
            # For now, just update last activity for API calls
            # In future, could track specific endpoint usage patterns
            update_data = {
                "$set": {
                    "usage_analytics.last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = self.users_collection.update_one(
                {"clerk_user_id": clerk_user_id},
                update_data
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {str(e)}")
            return False

def get_analytics_tracker():
    """Get AnalyticsTracker instance"""
    try:
        from utils.database import get_database
        db = get_database()
        return AnalyticsTracker(db)
    except Exception as e:
        logger.error(f"Failed to get analytics tracker: {str(e)}")
        return None

def track_activity(activity_type: str, **kwargs):
    """Decorator to automatically track user activities"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **func_kwargs):
            try:
                # Execute the original function first
                result = f(*args, **func_kwargs)
                
                # Get clerk_user_id from various sources
                clerk_user_id = None
                
                # Try from request headers
                if hasattr(request, 'headers'):
                    clerk_user_id = request.headers.get('X-Clerk-User-Id')
                
                # Try from request args
                if not clerk_user_id and hasattr(request, 'args'):
                    clerk_user_id = request.args.get('clerk_user_id')
                
                # Try from request json
                if not clerk_user_id and hasattr(request, 'get_json'):
                    json_data = request.get_json()
                    if json_data:
                        clerk_user_id = json_data.get('clerk_user_id')
                
                # Try from global context
                if not clerk_user_id and hasattr(g, 'clerk_user_id'):
                    clerk_user_id = g.clerk_user_id
                
                # Track activity if we have user ID
                if clerk_user_id:
                    tracker = get_analytics_tracker()
                    if tracker:
                        if activity_type == 'model_training':
                            training_time = kwargs.get('training_time', 0)
                            model_data = kwargs.get('model_data', {})
                            tracker.track_model_training(clerk_user_id, training_time, model_data)
                        elif activity_type == 'simulation_run':
                            execution_time = kwargs.get('execution_time', 0)
                            simulation_data = kwargs.get('simulation_data', {})
                            tracker.track_simulation_run(clerk_user_id, execution_time, simulation_data)
                        elif activity_type == 'file_upload':
                            file_size = kwargs.get('file_size', 0)
                            file_type = kwargs.get('file_type', 'unknown')
                            tracker.track_file_upload(clerk_user_id, file_size, file_type)
                        elif activity_type == 'api_usage':
                            endpoint = request.endpoint or 'unknown'
                            method = request.method or 'GET'
                            status_code = getattr(result, 'status_code', 200)
                            tracker.track_api_usage(clerk_user_id, endpoint, method, status_code)
                        else:
                            # Generic session tracking
                            tracker.track_user_session(clerk_user_id)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in activity tracking decorator: {str(e)}")
                # Return original result even if tracking fails
                return f(*args, **func_kwargs)
        
        return decorated_function
    return decorator

def track_dashboard_access():
    """Middleware to track dashboard access"""
    def middleware():
        # Get user ID from request
        clerk_user_id = (
            request.headers.get('X-Clerk-User-Id') or 
            request.args.get('clerk_user_id')
        )
        
        if clerk_user_id:
            tracker = get_analytics_tracker()
            if tracker:
                tracker.track_user_session(clerk_user_id)
    
    return middleware

# Usage tracking utilities
class UsageTracker:
    """Utility class for tracking specific usage patterns"""
    
    @staticmethod
    def track_model_performance(clerk_user_id: str, model_id: str, performance_metrics: Dict[str, float]):
        """Track model performance metrics for analytics"""
        try:
            tracker = get_analytics_tracker()
            if tracker:
                # Store performance data for trend analysis
                performance_data = {
                    "model_id": model_id,
                    "metrics": performance_metrics,
                    "timestamp": datetime.utcnow()
                }
                
                # Update user's model performance history
                tracker.db.user_model_performance.insert_one({
                    "clerk_user_id": clerk_user_id,
                    **performance_data
                })
                
                logger.info(f"Tracked model performance for {clerk_user_id}: {model_id}")
                return True
        
        except Exception as e:
            logger.error(f"Error tracking model performance: {str(e)}")
            return False
    
    @staticmethod
    def track_simulation_complexity(clerk_user_id: str, simulation_id: str, complexity_metrics: Dict[str, Any]):
        """Track simulation complexity for analytics"""
        try:
            tracker = get_analytics_tracker()
            if tracker:
                complexity_data = {
                    "simulation_id": simulation_id,
                    "metrics": complexity_metrics,
                    "timestamp": datetime.utcnow()
                }
                
                tracker.db.user_simulation_complexity.insert_one({
                    "clerk_user_id": clerk_user_id,
                    **complexity_data
                })
                
                logger.info(f"Tracked simulation complexity for {clerk_user_id}: {simulation_id}")
                return True
        
        except Exception as e:
            logger.error(f"Error tracking simulation complexity: {str(e)}")
            return False
    
    @staticmethod
    def get_usage_trends(clerk_user_id: str, days: int = 30):
        """Get user usage trends for the specified number of days"""
        try:
            tracker = get_analytics_tracker()
            if not tracker:
                return {}
            
            start_date = datetime.utcnow() - datetime.timedelta(days=days)
            
            # Get daily activity counts
            pipeline = [
                {
                    "$match": {
                        "clerk_user_id": clerk_user_id,
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "models_count": {
                            "$sum": {
                                "$cond": [{"$ne": ["$model_name", None]}, 1, 0]
                            }
                        },
                        "simulations_count": {
                            "$sum": {
                                "$cond": [{"$ne": ["$simulation_name", None]}, 1, 0]
                            }
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            # This would need to be adapted to work with separate collections
            # For now, return basic trend data
            trends = {
                "daily_models": [],
                "daily_simulations": [],
                "total_days": days,
                "period_start": start_date.isoformat()
            }
            
            return trends
        
        except Exception as e:
            logger.error(f"Error getting usage trends: {str(e)}")
            return {}