"""
User Routes for PhysicsLab Application
Handles user synchronization, dashboard data, and analytics
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Import our models and database utilities
try:
    from models.user import User, UserCreate, UserUpdate, UserService, UserResponse
    from utils.database import get_database
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
def get_dashboard():
    """
    Get user dashboard data (requires clerk_user_id in headers or query params)
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
        
        # Prepare dashboard data
        dashboard_data = {
            "user": {
                "name": user.name,
                "email": user.email,
                "member_since": user.created_at.isoformat()
            },
            "quick_stats": {
                "models_count": user.usage_analytics.total_models_trained,
                "simulations_count": user.usage_analytics.total_simulations_run,
                "total_training_time": format_time(user.usage_analytics.total_training_time),
                "storage_used": "0 MB"  # TODO: Calculate actual storage usage
            },
            "recent_activity": {
                "recent_models": [],  # TODO: Implement when ML models collection is ready
                "recent_simulations": []  # TODO: Implement when simulations collection is ready
            },
            "usage_analytics": {
                "models_this_month": 0,  # TODO: Calculate monthly stats
                "simulations_this_month": 0,  # TODO: Calculate monthly stats
                "avg_training_time": 0,  # TODO: Calculate average
                "last_activity": user.usage_analytics.last_activity.isoformat() if user.usage_analytics.last_activity else None
            }
        }
        
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

def format_time(seconds):
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"