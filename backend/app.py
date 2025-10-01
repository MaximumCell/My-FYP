# Main App Entry Point
import sys
import os
# Ensure the repository root is on sys.path so imports like `import backend.xxx` work
# whether the app is run from the repo root or from the backend/ subdirectory.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
# Also make sure the backend directory itself is available for local imports
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask
from flask_cors import CORS
from routes.ml_routes import ml_bp
from routes.simulation_routes import simulation_bp
from routes.ai_routes import ai_bp
from routes.user_routes import user_bp
from routes.model_management import model_bp
from routes.simulation_management import simulation_bp as simulation_mgmt_bp
from routes.materials_routes import materials_bp
from routes.books_routes import bp as books_bp
from routes.physics_advanced_routes import physics_bp as physics_advanced_bp
from utils.database import init_database, close_database, get_database
from utils.error_middleware import setup_error_handlers, get_error_stats
from utils.retry_mechanisms import with_database_retry
from utils.performance_optimization import (
    setup_performance_monitoring, 
    optimize_database_performance,
    get_cache_stats,
    get_performance_stats
)
from datetime import datetime
import atexit
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with more specific settings
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-User-ID", "X-Clerk-User-ID"]
    }
})

# Set up comprehensive error handling
setup_error_handlers(app)

# Set up performance monitoring
setup_performance_monitoring(app)

# Initialize database connection when app starts with retry logic
@with_database_retry
def initialize_database():
    """Initialize database connection when app starts with retry mechanism"""
    try:
        if init_database():
            logger.info("Database initialized successfully")
            return True
        else:
            logger.warning("Failed to initialize database - running without database features")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise  # Let retry mechanism handle this

# Call initialization
db_available = initialize_database()

# Optimize database performance if available
if db_available:
    try:
        db = get_database()
        optimization_result = optimize_database_performance(db)
        logger.info(f"Database optimization completed: {len(optimization_result.get('indexes_created', []))} indexes created")
    except Exception as e:
        logger.warning(f"Database optimization failed: {str(e)}")

# Register cleanup function
def cleanup():
    """Cleanup function to close database connection"""
    close_database()

atexit.register(cleanup)

# Register blueprints
app.register_blueprint(ml_bp, url_prefix='/ml')
app.register_blueprint(simulation_bp, url_prefix='/simulation')  # Restore prefix for existing routes
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(user_bp, url_prefix='/api/users')  # New user routes
app.register_blueprint(model_bp)  # Model management routes (already includes /api/models prefix)
app.register_blueprint(simulation_mgmt_bp)  # Simulation management routes (already includes /api/simulations prefix)
app.register_blueprint(materials_bp)
app.register_blueprint(books_bp)  # Physics books routes (includes /api/books prefix)
app.register_blueprint(physics_advanced_bp)  # Phase 7.3 advanced physics routes

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try to get database status
        db_status = "connected"
        db_latency = None
        try:
            db = get_database()
            import time
            start = time.time()
            db.command('ping')
            db_latency = round((time.time() - start) * 1000, 2)  # ms
        except Exception as e:
            db_status = "disconnected"
            logger.warning(f"Database health check failed: {str(e)}")
        
        return {
            "status": "healthy", 
            "message": "PhysicsLab API is running",
            "database": {
                "status": db_status,
                "latency_ms": db_latency
            },
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }, 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

# Error statistics endpoint
@app.route('/api/system/errors', methods=['GET'])
def error_statistics():
    """Get error statistics for monitoring"""
    try:
        stats = get_error_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }, 200
    except Exception as e:
        logger.error(f"Error statistics endpoint failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

# Performance statistics endpoint
@app.route('/api/system/performance', methods=['GET'])
def performance_statistics():
    """Get performance statistics for monitoring"""
    try:
        stats = get_performance_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }, 200
    except Exception as e:
        logger.error(f"Performance statistics endpoint failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

# Cache statistics endpoint
@app.route('/api/system/cache', methods=['GET'])
def cache_statistics():
    """Get cache statistics for monitoring"""
    try:
        stats = get_cache_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }, 200
    except Exception as e:
        logger.error(f"Cache statistics endpoint failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

if __name__ == '__main__':
    app.run(debug=True)
