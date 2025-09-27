"""
Cloudinary Configuration and Utilities
Handles file uploads to Cloudinary with proper folder structure and naming conventions
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import time
import re
from typing import Optional, Dict, Any, Tuple
import logging

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Constants
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB default
ALLOWED_FILE_TYPES = {
    'models': ['pkl', 'keras', 'h5'],
    'simulations': ['html', 'png'],
    'general': ['pkl', 'keras', 'h5', 'html', 'png']
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudinaryConfig:
    """Cloudinary configuration and utility class"""
    
    @staticmethod
    def test_connection() -> bool:
        """Test Cloudinary connection"""
        try:
            cloudinary.api.ping()
            logger.info("Cloudinary connection successful")
            return True
        except Exception as e:
            logger.error(f"Cloudinary connection failed: {str(e)}")
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to be Cloudinary-friendly
        - Convert to lowercase
        - Replace spaces with underscores
        - Remove special characters except underscores and hyphens
        """
        # Convert to lowercase and replace spaces
        filename = filename.lower().replace(' ', '_')
        
        # Remove file extension for processing
        name_part = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        
        # Keep only alphanumeric characters, underscores, and hyphens
        name_part = re.sub(r'[^a-z0-9_-]', '', name_part)
        
        # Remove multiple consecutive underscores
        name_part = re.sub(r'_+', '_', name_part)
        
        # Remove leading/trailing underscores
        name_part = name_part.strip('_')
        
        return name_part + extension
    
    @staticmethod
    def generate_public_id(user_id: str, filename: str, file_type: str) -> str:
        """
        Generate Cloudinary public_id with proper folder structure
        Format: physics-lab/{file_type}/user_{user_id}/{sanitized_filename}_{timestamp}
        """
        sanitized_name = CloudinaryConfig.sanitize_filename(filename)
        timestamp = int(time.time() * 1000)  # Milliseconds for uniqueness
        
        # Remove file extension from sanitized name for public_id
        name_without_ext = os.path.splitext(sanitized_name)[0]
        
        return f"physics-lab/{file_type}/user_{user_id}/{name_without_ext}_{timestamp}"
    
    @staticmethod
    def validate_file(file_data: bytes, filename: str, allowed_types: list) -> Tuple[bool, str]:
        """
        Validate file before upload
        Returns (is_valid, error_message)
        """
        # Check file size
        if len(file_data) > MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB."
        
        # Check file extension
        file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if file_extension not in allowed_types:
            return False, f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        
        return True, ""
    
    @staticmethod
    def get_folder_info(public_id: str) -> Dict[str, Any]:
        """
        Extract folder information from public_id
        Returns folder path and file info
        """
        parts = public_id.split('/')
        if len(parts) >= 4:
            return {
                'base_folder': parts[0],  # physics-lab
                'file_type': parts[1],    # models or simulations
                'user_folder': parts[2],  # user_{user_id}
                'filename': parts[3] if len(parts) > 3 else ''
            }
        return {}


# Utility functions for easy access
def test_cloudinary_connection():
    """Test Cloudinary connection - utility function"""
    return CloudinaryConfig.test_connection()


def get_cloudinary_config():
    """Get current Cloudinary configuration"""
    return {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'max_file_size': MAX_FILE_SIZE,
        'allowed_types': ALLOWED_FILE_TYPES
    }


# Test the configuration when module is imported
if __name__ == "__main__":
    print("Testing Cloudinary configuration...")
    if test_cloudinary_connection():
        print("✅ Cloudinary configuration is working!")
        print("Configuration:", get_cloudinary_config())
    else:
        print("❌ Cloudinary configuration failed!")