"""
MongoDB Database Connection and Configuration
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/physicslab')
        self.database_name = os.getenv('DB_NAME', 'physicslab')
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            # Try different connection methods
            connection_attempts = [
                # Attempt 1: With SSL parameters
                {
                    'uri': self.mongodb_uri,
                    'options': {
                        'serverSelectionTimeoutMS': 5000,
                        'ssl': True,
                        'tlsAllowInvalidCertificates': True,
                        'tlsAllowInvalidHostnames': True
                    }
                },
                # Attempt 2: Without extra SSL parameters (let URI handle it)
                {
                    'uri': self.mongodb_uri,
                    'options': {
                        'serverSelectionTimeoutMS': 10000
                    }
                },
                # Attempt 3: Fallback to local MongoDB if available
                {
                    'uri': 'mongodb://localhost:27017/physicslab',
                    'options': {
                        'serverSelectionTimeoutMS': 3000
                    }
                }
            ]
            
            for i, attempt in enumerate(connection_attempts):
                try:
                    logger.info(f"Connection attempt {i+1}...")
                    self.client = MongoClient(attempt['uri'], **attempt['options'])
                    
                    # Test the connection
                    self.client.admin.command('ping')
                    self.db = self.client[self.database_name]
                    
                    logger.info(f"Successfully connected to MongoDB: {self.database_name}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Connection attempt {i+1} failed: {str(e)}")
                    if self.client:
                        self.client.close()
                        self.client = None
                    continue
            
            logger.error("All connection attempts failed")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error in connection process: {str(e)}")
            return False
    
    def get_database(self):
        """Get database instance"""
        if self.db is None:
            if not self.connect():
                raise Exception("Database connection failed")
        return self.db
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db_config = DatabaseConfig()

def get_database():
    """Get database instance - use this in your routes"""
    return db_config.get_database()

def init_database():
    """Initialize database connection - call this when app starts"""
    return db_config.connect()

def close_database():
    """Close database connection - call this when app shuts down"""
    db_config.close_connection()