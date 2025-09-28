"""
MongoDB Database Connection and Configuration with Retry Logic
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging
import time

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
        """Establish connection to MongoDB with enhanced retry logic"""
        max_retries = 3
        base_delay = 1.0
        
        for retry in range(max_retries):
            try:
                # Try different connection methods
                connection_attempts = [
                    # Attempt 1: With SSL parameters
                    {
                        'uri': self.mongodb_uri,
                        'options': {
                            'serverSelectionTimeoutMS': 8000,
                            'connectTimeoutMS': 10000,
                            'socketTimeoutMS': 10000,
                            'ssl': True,
                            'tlsAllowInvalidCertificates': True,
                            'tlsAllowInvalidHostnames': True,
                            'retryWrites': True,
                            'retryReads': True
                        }
                    },
                    # Attempt 2: Without extra SSL parameters (let URI handle it)
                    {
                        'uri': self.mongodb_uri,
                        'options': {
                            'serverSelectionTimeoutMS': 10000,
                            'connectTimeoutMS': 15000,
                            'socketTimeoutMS': 15000,
                            'retryWrites': True,
                            'retryReads': True
                        }
                    },
                    # Attempt 3: Fallback to local MongoDB if available
                    {
                        'uri': 'mongodb://localhost:27017/physicslab',
                        'options': {
                            'serverSelectionTimeoutMS': 3000,
                            'connectTimeoutMS': 5000,
                            'socketTimeoutMS': 5000
                        }
                    }
                ]
                
                for i, attempt in enumerate(connection_attempts):
                    try:
                        logger.info(f"Connection attempt {i+1} (retry {retry+1}/{max_retries})...")
                        self.client = MongoClient(attempt['uri'], **attempt['options'])
                        
                        # Test the connection with ping
                        start_time = time.time()
                        self.client.admin.command('ping')
                        ping_time = (time.time() - start_time) * 1000
                        
                        self.db = self.client[self.database_name]
                        
                        # Test database access
                        self.db.list_collection_names()
                        
                        logger.info(f"Successfully connected to MongoDB: {self.database_name} (ping: {ping_time:.2f}ms)")
                        return True
                        
                    except Exception as e:
                        logger.warning(f"Connection attempt {i+1} failed: {str(e)}")
                        if self.client:
                            try:
                                self.client.close()
                            except:
                                pass
                            self.client = None
                        continue
                
                # If we reach here, all connection attempts failed for this retry
                if retry < max_retries - 1:
                    delay = base_delay * (2 ** retry)  # Exponential backoff
                    logger.info(f"Retrying database connection in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("All connection attempts failed after all retries")
                    return False
                    
            except Exception as e:
                logger.error(f"Unexpected error in connection process (retry {retry+1}): {str(e)}")
                if retry < max_retries - 1:
                    delay = base_delay * (2 ** retry)
                    time.sleep(delay)
                else:
                    return False
        
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