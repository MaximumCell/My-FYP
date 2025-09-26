"""
Comprehensive Error Handling for Cloudinary Operations
Provides standardized error responses and logging for the PhysicsLab application
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standardized error codes for Cloudinary operations"""
    
    # File validation errors
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    EMPTY_FILE = "EMPTY_FILE"
    INVALID_FILENAME = "INVALID_FILENAME"
    
    # Upload errors
    UPLOAD_FAILED = "UPLOAD_FAILED"
    NETWORK_ERROR = "NETWORK_ERROR"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    
    # Download errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    ACCESS_DENIED = "ACCESS_DENIED"
    URL_GENERATION_FAILED = "URL_GENERATION_FAILED"
    
    # Database errors
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class CloudinaryErrorHandler:
    """Centralized error handling for Cloudinary operations"""
    
    @staticmethod
    def format_error_response(
        error_code: ErrorCode,
        message: str,
        details: Optional[str] = None,
        http_status: int = 400
    ) -> Dict[str, Any]:
        """
        Format a standardized error response
        
        Args:
            error_code: Standardized error code
            message: User-friendly error message
            details: Additional technical details (optional)
            http_status: HTTP status code
            
        Returns:
            Formatted error response dictionary
        """
        response = {
            "success": False,
            "error": {
                "code": error_code.value,
                "message": message,
                "http_status": http_status
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        # Log the error
        log_message = f"Error {error_code.value}: {message}"
        if details:
            log_message += f" | Details: {details}"
            
        if http_status >= 500:
            logger.error(log_message)
        else:
            logger.warning(log_message)
            
        return response
    
    @staticmethod
    def handle_file_validation_error(error_message: str) -> Dict[str, Any]:
        """Handle file validation errors"""
        
        if "too large" in error_message.lower():
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_TOO_LARGE,
                "File size exceeds the maximum allowed limit of 50MB. Please compress your file or use a smaller dataset.",
                error_message,
                413  # Payload Too Large
            )
        
        elif "invalid file type" in error_message.lower():
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INVALID_FILE_TYPE,
                "File type not supported. Please upload only .pkl files for models or .html/.png files for simulations.",
                error_message,
                415  # Unsupported Media Type
            )
        
        elif "empty" in error_message.lower():
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.EMPTY_FILE,
                "File appears to be empty. Please check your file and try again.",
                error_message,
                400
            )
        
        else:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.VALIDATION_ERROR,
                "File validation failed. Please check your file and try again.",
                error_message,
                400
            )
    
    @staticmethod
    def handle_upload_error(error_message: str) -> Dict[str, Any]:
        """Handle file upload errors"""
        
        error_lower = error_message.lower()
        
        if "network" in error_lower or "connection" in error_lower or "timeout" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.NETWORK_ERROR,
                "Network connection issue. Please check your internet connection and try again.",
                error_message,
                503  # Service Unavailable
            )
        
        elif "quota" in error_lower or "limit" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.QUOTA_EXCEEDED,
                "Storage quota exceeded. Please delete some files or contact support to increase your storage limit.",
                error_message,
                507  # Insufficient Storage
            )
        
        elif "unauthorized" in error_lower or "authentication" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.AUTHENTICATION_ERROR,
                "Authentication failed. Please contact support if this issue persists.",
                error_message,
                401  # Unauthorized
            )
        
        else:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.UPLOAD_FAILED,
                "File upload failed. Please try again later. If the problem persists, contact support.",
                error_message,
                500  # Internal Server Error
            )
    
    @staticmethod
    def handle_download_error(error_message: str) -> Dict[str, Any]:
        """Handle file download errors"""
        
        error_lower = error_message.lower()
        
        if "not found" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.FILE_NOT_FOUND,
                "Requested file not found. It may have been deleted or moved.",
                error_message,
                404  # Not Found
            )
        
        elif "access denied" in error_lower or "forbidden" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.ACCESS_DENIED,
                "Access to this file is denied. Please check your permissions.",
                error_message,
                403  # Forbidden
            )
        
        elif "url generation" in error_lower:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.URL_GENERATION_FAILED,
                "Failed to generate download URL. Please try again later.",
                error_message,
                500
            )
        
        else:
            return CloudinaryErrorHandler.format_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Download failed due to an internal error. Please try again later.",
                error_message,
                500
            )
    
    @staticmethod
    def format_success_response(data: Dict[str, Any], message: str = "Operation completed successfully") -> Dict[str, Any]:
        """
        Format a standardized success response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted success response dictionary
        """
        return {
            "success": True,
            "message": message,
            "data": data
        }


# Convenience functions for common error scenarios
def file_too_large_error(max_size_mb: int = 50):
    """Generate file too large error response"""
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.FILE_TOO_LARGE,
        f"File too large. Maximum size is {max_size_mb}MB.",
        http_status=413
    )

def invalid_file_type_error(allowed_types: list):
    """Generate invalid file type error response"""
    types_str = ", ".join(allowed_types)
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.INVALID_FILE_TYPE,
        f"Invalid file type. Allowed types: {types_str}",
        http_status=415
    )

def upload_failed_error(details: str = None):
    """Generate upload failed error response"""
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.UPLOAD_FAILED,
        "File upload failed. Please try again later.",
        details,
        500
    )