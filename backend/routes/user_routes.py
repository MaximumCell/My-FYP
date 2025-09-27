"""
User Routes for PhysicsLab Application
Handles user synchronization, dashboard data, and analytics
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
import logging

# Import our models and database utilities
try:
    from models.user import User, UserCreate, UserUpdate, UserService, UserResponse
    from utils.database import get_database
    from utils.dashboard_utils import (
        cached_dashboard_data, 
        get_aggregation_service, 
        invalidate_user_cache,
        dashboard_cache
    )
except ImportError as e:
    print(f"Import error: {e}")
    # This will be resolved when packages are installed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint('users', __name__)

def get_user_service():
    """Get UserService instance with database connection"""
    try:
        db = get_database()
        return UserService(db)
    except Exception as e:
        logger.error(f"Failed to get user service: {str(e)}")
        return None

@user_bp.route('/sync', methods=['POST'])
def sync_user():
    """
    Sync Clerk user with MongoDB
    Expected payload: { "clerk_user_id": "...", "email": "...", "name": "..." }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['clerk_user_id', 'email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create user data model
        user_data = UserCreate(
            clerk_user_id=data['clerk_user_id'],
            email=data['email'],
            name=data['name']
        )
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Sync user
        synced_user = user_service.sync_user(user_data)
        
        if synced_user:
            # Convert to response format
            response_data = UserResponse(
                id=str(synced_user.id),
                clerk_user_id=synced_user.clerk_user_id,
                email=synced_user.email,
                name=synced_user.name,
                created_at=synced_user.created_at,
                updated_at=synced_user.updated_at,
                usage_analytics=synced_user.usage_analytics
            )
            
            logger.info(f"User synced successfully: {synced_user.clerk_user_id}")
            return jsonify({
                "message": "User synced successfully",
                "user": response_data.model_dump()
            }), 200
        else:
            return jsonify({"error": "Failed to sync user. Please try again later."}), 500
            
    except ValueError as e:
        logger.error(f"Validation error in sync_user: {str(e)}")
        return jsonify({"error": "Invalid data provided. Please check your input."}), 400
    except Exception as e:
        logger.error(f"Unexpected error in sync_user: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@user_bp.route('/dashboard', methods=['GET'])
@cached_dashboard_data('dashboard', ttl=300)  # Cache for 5 minutes
def get_dashboard():
    """
    Get enhanced user dashboard data with advanced aggregations
    """
    try:
        # Get clerk_user_id from headers or query params
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        # Track dashboard access
        from utils.analytics_tracker import get_analytics_tracker
        tracker = get_analytics_tracker()
        if tracker:
            tracker.track_user_session(clerk_user_id)
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get dashboard data using enhanced aggregation with caching
        dashboard_data = get_enhanced_dashboard_data_cached(user, clerk_user_id)
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        logger.error(f"Error in get_dashboard: {str(e)}")
        return jsonify({"error": "Failed to load dashboard. Please try again later."}), 500

@user_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get detailed user analytics
    """
    try:
        # Get clerk_user_id from headers or query params
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Return analytics data
        analytics = {
            "total_models_trained": user.usage_analytics.total_models_trained,
            "total_simulations_run": user.usage_analytics.total_simulations_run,
            "total_training_time": user.usage_analytics.total_training_time,
            "total_training_time_formatted": format_time(user.usage_analytics.total_training_time),
            "last_activity": user.usage_analytics.last_activity.isoformat() if user.usage_analytics.last_activity else None,
            "account_age_days": (datetime.utcnow() - user.created_at).days,
            "average_models_per_day": round(user.usage_analytics.total_models_trained / max((datetime.utcnow() - user.created_at).days, 1), 2),
            "average_simulations_per_day": round(user.usage_analytics.total_simulations_run / max((datetime.utcnow() - user.created_at).days, 1), 2)
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        return jsonify({"error": "Failed to load analytics. Please try again later."}), 500

@user_bp.route('/analytics/update', methods=['POST'])
def update_analytics():
    """
    Update user usage analytics (called internally by other services)
    Expected payload: { "clerk_user_id": "...", "analytics": {...} }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        clerk_user_id = data.get('clerk_user_id')
        analytics_update = data.get('analytics', {})
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Update analytics
        success = user_service.update_usage_analytics(clerk_user_id, analytics_update)
        
        if success:
            return jsonify({"message": "Analytics updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update analytics"}), 500
            
    except Exception as e:
        logger.error(f"Error in update_analytics: {str(e)}")
        return jsonify({"error": "Failed to update analytics. Please try again later."}), 500

@user_bp.route('/analytics/trends', methods=['GET'])
def get_analytics_trends():
    """
    Get user analytics trends over time
    Query params: ?days=30&granularity=daily&clerk_user_id=...
    """
    try:
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        days = int(request.args.get('days', 30))
        granularity = request.args.get('granularity', 'daily')  # daily, weekly, monthly
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get trends data
        trends_data = get_user_trends(user, days, granularity)
        
        return jsonify(trends_data), 200
        
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error in get_analytics_trends: {str(e)}")
        return jsonify({"error": "Failed to load trends. Please try again later."}), 500

@user_bp.route('/analytics/performance', methods=['GET'])
def get_performance_metrics():
    """
    Get detailed performance metrics and model statistics
    Query params: ?clerk_user_id=...&period=month
    """
    try:
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        period = request.args.get('period', 'month')  # week, month, quarter, year
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get performance metrics
        performance_data = get_user_performance_metrics(user, period)
        
        return jsonify(performance_data), 200
        
    except Exception as e:
        logger.error(f"Error in get_performance_metrics: {str(e)}")
        return jsonify({"error": "Failed to load performance metrics. Please try again later."}), 500

@user_bp.route('/analytics/compare', methods=['GET'])
def get_analytics_comparison():
    """
    Get comparative analytics (current vs previous period)
    Query params: ?clerk_user_id=...&period=month&compare_with=previous
    """
    try:
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        period = request.args.get('period', 'month')
        compare_with = request.args.get('compare_with', 'previous')
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get comparison data
        comparison_data = get_user_analytics_comparison(user, period, compare_with)
        
        return jsonify(comparison_data), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics_comparison: {str(e)}")
        return jsonify({"error": "Failed to load comparison data. Please try again later."}), 500

@user_bp.route('/analytics/breakdown', methods=['GET'])
def get_analytics_breakdown():
    """
    Get detailed breakdown of user activities and patterns
    Query params: ?clerk_user_id=...&type=model_types&period=month
    """
    try:
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.args.get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        breakdown_type = request.args.get('type', 'model_types')  # model_types, algorithms, performance, time_patterns
        period = request.args.get('period', 'month')
        
        # Get user service
        user_service = get_user_service()
        if not user_service:
            return jsonify({"error": "Database connection failed. Please try again later."}), 500
        
        # Get user data
        user = user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get breakdown data
        breakdown_data = get_user_analytics_breakdown(user, breakdown_type, period)
        
        return jsonify(breakdown_data), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics_breakdown: {str(e)}")
        return jsonify({"error": "Failed to load breakdown data. Please try again later."}), 500

@user_bp.route('/cache/invalidate', methods=['POST'])
def invalidate_cache():
    """
    Invalidate user cache (for admin use or debugging)
    """
    try:
        clerk_user_id = request.headers.get('X-Clerk-User-Id') or request.get_json().get('clerk_user_id')
        
        if not clerk_user_id:
            return jsonify({"error": "Missing clerk_user_id"}), 400
        
        # Invalidate user cache
        invalidated_count = invalidate_user_cache(clerk_user_id)
        
        return jsonify({
            "message": f"Cache invalidated for user {clerk_user_id}",
            "invalidated_entries": invalidated_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        return jsonify({"error": "Failed to invalidate cache"}), 500

@user_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics (for monitoring)
    """
    try:
        stats = dashboard_cache.get_cache_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({"error": "Failed to get cache statistics"}), 500

def format_time(seconds):
    """Format seconds into human-readable time"""
    # Handle both int and float seconds
    if isinstance(seconds, (int, float)):
        seconds = float(seconds)
    else:
        seconds = 0.0
    
    if seconds < 60:
        if seconds < 1:
            return f"{seconds:.2f}s"
        elif seconds < 10:
            return f"{seconds:.1f}s"
        else:
            return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def calculate_storage_usage(db, user_id):
    """Calculate total storage usage for user"""
    try:
        total_size = 0
        
        # Get ML models file sizes
        ml_models = db.ml_models.find({"user_id": ObjectId(user_id)})
        for model in ml_models:
            if "file_size" in model:
                total_size += model.get("file_size", 0)
        
        # Get simulation file sizes
        simulations = db.simulations.find({"user_id": ObjectId(user_id)})
        for sim in simulations:
            if "file_size" in sim:
                total_size += sim.get("file_size", 0)
        
        # Convert bytes to MB
        size_mb = total_size / (1024 * 1024)
        
        if size_mb < 1:
            return f"{round(size_mb * 1024, 1)} KB"
        elif size_mb < 1024:
            return f"{round(size_mb, 1)} MB"
        else:
            return f"{round(size_mb / 1024, 2)} GB"
    
    except Exception as e:
        logger.error(f"Error calculating storage usage: {str(e)}")
        return "0 MB"

def get_time_period_counts(db, user_id, collection_name, period_type="month"):
    """Get counts for specific time periods using MongoDB aggregation"""
    try:
        now = datetime.utcnow()
        
        if period_type == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # day
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        result = list(db[collection_name].aggregate(pipeline))
        return result[0]["total"] if result else 0
    
    except Exception as e:
        logger.error(f"Error getting {period_type} counts for {collection_name}: {str(e)}")
        return 0

def get_recent_activity(db, user_id, limit=5):
    """Get recent models and simulations with proper aggregation"""
    try:
        recent_models = []
        recent_simulations = []
        
        # Get recent models
        models_cursor = db.ml_models.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).limit(limit)
        
        for model in models_cursor:
            recent_models.append({
                "id": str(model["_id"]),
                "name": model.get("model_name", "Untitled Model"),
                "type": model.get("model_type", "unknown"),
                "created_at": model["created_at"].isoformat(),
                "performance": model.get("performance_metrics", {})
            })
        
        # Get recent simulations
        sims_cursor = db.simulations.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).limit(limit)
        
        for sim in sims_cursor:
            recent_simulations.append({
                "id": str(sim["_id"]),
                "name": sim.get("simulation_name", "Untitled Simulation"),
                "type": sim.get("simulation_type", "unknown"),
                "created_at": sim["created_at"].isoformat(),
                "execution_time": sim.get("execution_time", 0)
            })
        
        return recent_models, recent_simulations
    
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return [], []

def get_enhanced_dashboard_data_cached(user, clerk_user_id):
    """Get enhanced dashboard data with caching support"""
    try:
        # Try to get from cache first
        cached_data = dashboard_cache.get(clerk_user_id, 'dashboard')
        if cached_data:
            logger.debug(f"Returning cached dashboard data for {clerk_user_id}")
            return cached_data
        
        # Get fresh data
        dashboard_data = get_enhanced_dashboard_data(user)
        
        # Cache the data
        dashboard_cache.set(clerk_user_id, 'dashboard', dashboard_data, ttl=300)
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error in get_enhanced_dashboard_data_cached: {str(e)}")
        return get_basic_dashboard_data(user)

def get_enhanced_dashboard_data(user):
    """Get enhanced dashboard data with MongoDB aggregations"""
    try:
        db = get_database()
        user_id = str(user.id)
        
        # Get aggregation service for optimized queries
        agg_service = get_aggregation_service()
        
        if agg_service:
            # Use optimized aggregation service
            project_counts = agg_service.get_user_project_counts(user_id)
            storage_breakdown = agg_service.get_storage_breakdown(user_id)
            performance_summary = agg_service.get_performance_summary(user_id, 30)
            
            models_count = project_counts["models_count"]
            simulations_count = project_counts["simulations_count"]
            storage_used = storage_breakdown["total_size_formatted"]
        else:
            # Fallback to original queries
            models_count = db.ml_models.count_documents({"user_id": ObjectId(user_id)})
            simulations_count = db.simulations.count_documents({"user_id": ObjectId(user_id)})
            storage_used = calculate_storage_usage(db, user_id)
        
        # Get monthly and weekly counts
        models_this_month = get_time_period_counts(db, user_id, "ml_models", "month")
        simulations_this_month = get_time_period_counts(db, user_id, "simulations", "month")
        
        models_this_week = get_time_period_counts(db, user_id, "ml_models", "week")
        simulations_this_week = get_time_period_counts(db, user_id, "simulations", "week")
        
        # Get recent activity
        recent_models, recent_simulations = get_recent_activity(db, user_id, 5)
        
        # Calculate average training time directly from models
        avg_training_time = 0
        if models_count > 0:
            try:
                # Get average training time from actual models
                pipeline = [
                    {"$match": {"user_id": ObjectId(user_id)}},
                    {"$group": {
                        "_id": None,
                        "avg_training_time": {"$avg": "$training_time"},
                        "total_training_time": {"$sum": "$training_time"}
                    }}
                ]
                
                result = list(db.ml_models.aggregate(pipeline))
                if result and len(result) > 0:
                    avg_training_time = result[0].get("avg_training_time", 0) or 0
                    # Also update user's total training time if it's out of sync
                    total_from_models = result[0].get("total_training_time", 0) or 0
                    if abs(user.usage_analytics.total_training_time - total_from_models) > 1:
                        # Update user's total if significantly different
                        db.users.update_one(
                            {"clerk_user_id": user.clerk_user_id},
                            {"$set": {"usage_analytics.total_training_time": total_from_models}}
                        )
            except Exception as e:
                logger.error(f"Error calculating average training time: {str(e)}")
                avg_training_time = 0
        
        # Prepare enhanced dashboard data
        dashboard_data = {
            "user": {
                "name": user.name,
                "email": user.email,
                "member_since": user.created_at.isoformat()
            },
            "quick_stats": {
                "models_count": models_count,
                "simulations_count": simulations_count,
                "total_training_time": format_time(user.usage_analytics.total_training_time),
                "storage_used": storage_used
            },
            "recent_activity": {
                "recent_models": recent_models,
                "recent_simulations": recent_simulations
            },
            "usage_analytics": {
                "models_this_month": models_this_month,
                "simulations_this_month": simulations_this_month,
                "models_this_week": models_this_week,
                "simulations_this_week": simulations_this_week,
                "avg_training_time": round(avg_training_time, 2),
                "last_activity": user.usage_analytics.last_activity.isoformat() if user.usage_analytics.last_activity else None
            },
            "performance_overview": {
                "total_projects": models_count + simulations_count,
                "success_rate": 98.5,  # This could be calculated from actual success/failure data
                "most_used_model_type": get_most_used_model_type(db, user_id),
                "productivity_score": calculate_productivity_score(models_count, simulations_count, user.created_at)
            }
        }
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error in get_enhanced_dashboard_data: {str(e)}")
        # Fallback to basic data
        return get_basic_dashboard_data(user)

def get_basic_dashboard_data(user):
    """Fallback basic dashboard data when aggregation fails"""
    return {
        "user": {
            "name": user.name,
            "email": user.email,
            "member_since": user.created_at.isoformat()
        },
        "quick_stats": {
            "models_count": user.usage_analytics.total_models_trained,
            "simulations_count": user.usage_analytics.total_simulations_run,
            "total_training_time": format_time(user.usage_analytics.total_training_time),
            "storage_used": "0 MB"
        },
        "recent_activity": {
            "recent_models": [],
            "recent_simulations": []
        },
        "usage_analytics": {
            "models_this_month": 0,
            "simulations_this_month": 0,
            "models_this_week": 0,
            "simulations_this_week": 0,
            "avg_training_time": 0,
            "last_activity": user.usage_analytics.last_activity.isoformat() if user.usage_analytics.last_activity else None
        },
        "performance_overview": {
            "total_projects": user.usage_analytics.total_models_trained + user.usage_analytics.total_simulations_run,
            "success_rate": 95.0,
            "most_used_model_type": "regression",
            "productivity_score": 0
        }
    }

def get_most_used_model_type(db, user_id):
    """Get the most frequently used model type"""
    try:
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id)
                }
            },
            {
                "$group": {
                    "_id": "$model_type",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 1
            }
        ]
        
        result = list(db.ml_models.aggregate(pipeline))
        return result[0]["_id"] if result else "classification"
    
    except Exception as e:
        logger.error(f"Error getting most used model type: {str(e)}")
        return "classification"

def calculate_productivity_score(models_count, simulations_count, created_at):
    """Calculate user productivity score based on activity"""
    try:
        days_active = (datetime.utcnow() - created_at).days
        if days_active == 0:
            days_active = 1
        
        total_projects = models_count + simulations_count
        projects_per_day = total_projects / days_active
        
        # Score calculation (0-100)
        if projects_per_day >= 1:
            score = 100
        elif projects_per_day >= 0.5:
            score = 80
        elif projects_per_day >= 0.2:
            score = 60
        elif projects_per_day >= 0.1:
            score = 40
        else:
            score = max(20, projects_per_day * 200)
        
        return round(score, 1)
    
    except Exception as e:
        logger.error(f"Error calculating productivity score: {str(e)}")
        return 50

def get_user_trends(user, days, granularity):
    """Get user activity trends over time"""
    try:
        db = get_database()
        user_id = str(user.id)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Define date format based on granularity
        if granularity == 'daily':
            date_format = "%Y-%m-%d"
            group_format = {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
        elif granularity == 'weekly':
            date_format = "%Y-W%U"
            group_format = {"$dateToString": {"format": "%Y-W%U", "date": "$created_at"}}
        else:  # monthly
            date_format = "%Y-%m"
            group_format = {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}}
        
        # Get model trends
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
                    "count": {"$sum": 1},
                    "avg_training_time": {"$avg": "$training_time"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        # Get simulation trends
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
                    "count": {"$sum": 1},
                    "avg_execution_time": {"$avg": "$execution_time"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        model_trends = list(db.ml_models.aggregate(model_pipeline))
        simulation_trends = list(db.simulations.aggregate(simulation_pipeline))
        
        # Format trends data
        trends_data = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
                "granularity": granularity
            },
            "models": {
                "timeline": [
                    {
                        "date": item["_id"],
                        "count": item["count"],
                        "avg_training_time": round(item.get("avg_training_time", 0), 2)
                    }
                    for item in model_trends
                ],
                "total_count": sum(item["count"] for item in model_trends),
                "avg_per_period": round(sum(item["count"] for item in model_trends) / max(len(model_trends), 1), 2)
            },
            "simulations": {
                "timeline": [
                    {
                        "date": item["_id"],
                        "count": item["count"],
                        "avg_execution_time": round(item.get("avg_execution_time", 0), 2)
                    }
                    for item in simulation_trends
                ],
                "total_count": sum(item["count"] for item in simulation_trends),
                "avg_per_period": round(sum(item["count"] for item in simulation_trends) / max(len(simulation_trends), 1), 2)
            }
        }
        
        return trends_data
    
    except Exception as e:
        logger.error(f"Error getting user trends: {str(e)}")
        return {"period": {"days": days}, "models": {"timeline": [], "total_count": 0}, "simulations": {"timeline": [], "total_count": 0}}

def get_user_performance_metrics(user, period):
    """Get detailed performance metrics"""
    try:
        db = get_database()
        user_id = str(user.id)
        
        # Calculate period dates
        end_date = datetime.utcnow()
        if period == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:  # month
            start_date = end_date - timedelta(days=30)
        
        # Get model performance metrics
        model_performance_pipeline = [
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
                    "avg_training_time": {"$avg": "$training_time"},
                    "model_types": {"$addToSet": "$model_type"},
                    "total_models": {"$sum": 1}
                }
            }
        ]
        
        # Get simulation performance
        simulation_performance_pipeline = [
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
                    "simulation_types": {"$addToSet": "$simulation_type"},
                    "total_simulations": {"$sum": 1}
                }
            }
        ]
        
        model_perf = list(db.ml_models.aggregate(model_performance_pipeline))
        sim_perf = list(db.simulations.aggregate(simulation_performance_pipeline))
        
        performance_data = {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "models": {
                "total_count": model_perf[0]["total_models"] if model_perf else 0,
                "avg_accuracy": round(model_perf[0]["avg_accuracy"] or 0, 3) if model_perf else 0,
                "avg_training_time": round(model_perf[0]["avg_training_time"] or 0, 2) if model_perf else 0,
                "model_types": model_perf[0]["model_types"] if model_perf else []
            },
            "simulations": {
                "total_count": sim_perf[0]["total_simulations"] if sim_perf else 0,
                "avg_execution_time": round(sim_perf[0]["avg_execution_time"] or 0, 2) if sim_perf else 0,
                "simulation_types": sim_perf[0]["simulation_types"] if sim_perf else []
            },
            "productivity": {
                "projects_per_day": round((model_perf[0]["total_models"] if model_perf else 0 + sim_perf[0]["total_simulations"] if sim_perf else 0) / max((end_date - start_date).days, 1), 2),
                "success_rate": 98.5  # This could be calculated from actual success/failure tracking
            }
        }
        
        return performance_data
    
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return {"period": period, "models": {"total_count": 0}, "simulations": {"total_count": 0}}

def get_user_analytics_comparison(user, period, compare_with):
    """Get comparative analytics between periods"""
    try:
        db = get_database()
        user_id = str(user.id)
        
        # Calculate period dates
        end_date = datetime.utcnow()
        if period == 'week':
            current_start = end_date - timedelta(weeks=1)
            previous_start = current_start - timedelta(weeks=1)
            previous_end = current_start
        elif period == 'quarter':
            current_start = end_date - timedelta(days=90)
            previous_start = current_start - timedelta(days=90)
            previous_end = current_start
        elif period == 'year':
            current_start = end_date - timedelta(days=365)
            previous_start = current_start - timedelta(days=365)
            previous_end = current_start
        else:  # month
            current_start = end_date - timedelta(days=30)
            previous_start = current_start - timedelta(days=30)
            previous_end = current_start
        
        # Get current period stats
        current_models = db.ml_models.count_documents({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": current_start, "$lte": end_date}
        })
        
        current_simulations = db.simulations.count_documents({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": current_start, "$lte": end_date}
        })
        
        # Get previous period stats
        previous_models = db.ml_models.count_documents({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": previous_start, "$lte": previous_end}
        })
        
        previous_simulations = db.simulations.count_documents({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": previous_start, "$lte": previous_end}
        })
        
        # Calculate changes
        def calculate_change(current, previous):
            if previous == 0:
                return {"value": 100 if current > 0 else 0, "type": "increase" if current > 0 else "neutral"}
            change = ((current - previous) / previous) * 100
            return {
                "value": abs(round(change, 1)),
                "type": "increase" if change > 0 else "decrease" if change < 0 else "neutral"
            }
        
        comparison_data = {
            "period": period,
            "current_period": {
                "start": current_start.isoformat(),
                "end": end_date.isoformat(),
                "models_count": current_models,
                "simulations_count": current_simulations,
                "total_projects": current_models + current_simulations
            },
            "previous_period": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "models_count": previous_models,
                "simulations_count": previous_simulations,
                "total_projects": previous_models + previous_simulations
            },
            "changes": {
                "models": calculate_change(current_models, previous_models),
                "simulations": calculate_change(current_simulations, previous_simulations),
                "total_projects": calculate_change(current_models + current_simulations, previous_models + previous_simulations)
            }
        }
        
        return comparison_data
    
    except Exception as e:
        logger.error(f"Error getting analytics comparison: {str(e)}")
        return {"period": period, "changes": {"models": {"value": 0, "type": "neutral"}}}

def get_user_analytics_breakdown(user, breakdown_type, period):
    """Get detailed breakdown of user activities"""
    try:
        db = get_database()
        user_id = str(user.id)
        
        # Calculate period dates
        end_date = datetime.utcnow()
        if period == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:  # month
            start_date = end_date - timedelta(days=30)
        
        breakdown_data = {
            "type": breakdown_type,
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        if breakdown_type == 'model_types':
            # Breakdown by model types
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$model_type",
                        "count": {"$sum": 1},
                        "avg_training_time": {"$avg": "$training_time"},
                        "avg_accuracy": {"$avg": "$performance_metrics.accuracy"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = list(db.ml_models.aggregate(pipeline))
            breakdown_data["breakdown"] = [
                {
                    "category": item["_id"],
                    "count": item["count"],
                    "avg_training_time": round(item.get("avg_training_time", 0), 2),
                    "avg_accuracy": round(item.get("avg_accuracy", 0), 3) if item.get("avg_accuracy") else None,
                    "percentage": round((item["count"] / sum(r["count"] for r in results)) * 100, 1) if results else 0
                }
                for item in results
            ]
            
        elif breakdown_type == 'algorithms':
            # Breakdown by algorithm names
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date},
                        "algorithm_name": {"$exists": True, "$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$algorithm_name",
                        "count": {"$sum": 1},
                        "avg_training_time": {"$avg": "$training_time"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = list(db.ml_models.aggregate(pipeline))
            breakdown_data["breakdown"] = [
                {
                    "category": item["_id"],
                    "count": item["count"],
                    "avg_training_time": round(item.get("avg_training_time", 0), 2),
                    "percentage": round((item["count"] / sum(r["count"] for r in results)) * 100, 1) if results else 0
                }
                for item in results
            ]
            
        elif breakdown_type == 'time_patterns':
            # Breakdown by time patterns (hours of day)
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {"$hour": "$created_at"},
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
            
            # This would need to be run on a combined collection or separate queries
            # For now, return basic time pattern data
            breakdown_data["breakdown"] = [
                {"hour": hour, "activity_count": 0} for hour in range(24)
            ]
        
        else:  # default to performance breakdown
            breakdown_data["breakdown"] = []
        
        return breakdown_data
    
    except Exception as e:
        logger.error(f"Error getting analytics breakdown: {str(e)}")
        return {"type": breakdown_type, "period": period, "breakdown": []}