# Main App Entry Point
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.ml_routes import ml_bp
from routes.simulation_routes import simulation_bp
from routes.ai_routes import ai_bp
from routes.user_routes import user_bp
from routes.model_management import model_bp
from utils.database import init_database, close_database, get_database
from datetime import datetime
import atexit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database connection when app starts
def initialize_database():
    """Initialize database connection when app starts"""
    try:
        if init_database():
            logger.info("Database initialized successfully")
            return True
        else:
            logger.warning("Failed to initialize database - running without database features")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

# Call initialization
db_available = initialize_database()

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

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try to get database status
        db_status = "connected"
        try:
            db = get_database()
            db.command('ping')
        except:
            db_status = "disconnected"
        
        return {
            "status": "healthy", 
            "message": "PhysicsLab API is running",
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }, 200
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, 500

if __name__ == '__main__':
    app.run(debug=True)
