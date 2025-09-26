"""
Simple Flask app test without database dependencies
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Simple health check
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "PhysicsLab API is running"}, 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return {"message": "Welcome to PhysicsLab API", "version": "1.0.0"}, 200

if __name__ == '__main__':
    logger.info("Starting simple Flask app...")
    app.run(debug=True, port=5001)  # Use different port to avoid conflicts