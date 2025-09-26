"""
Comprehensive Error Handling for Cloudinary Operations
Provides structured error handling with user-friendly messages and detailed logging
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
import cloudinary.exceptions

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standardized error codes for different types of failures"""
    
    # File validation errors
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    EMPTY_FILE = "EMPTY_FILE"
    CORRUPTED_FILE = "CORRUPTED_FILE"
    
    # Upload errors
    UPLOAD_FAILED = "UPLOAD_FAILED"
    NETWORK_ERROR = "NETWORK_ERROR"
    STORAGE_QUOTA_EXCEEDED = "STORAGE_QUOTA_EXCEEDED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    
    # Download errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    ACCESS_DENIED = "ACCESS_DENIED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class CloudinaryError(Exception):
    """Base exception class for Cloudinary operations with structured error handling"""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode, 
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or self._get_user_friendly_message()
        
        super().__init__(self.message)
    
    def _get_user_friendly_message(self) -> str:
        """Generate user-friendly error message based on error code"""
        
        user_messages = {
            ErrorCode.FILE_TOO_LARGE: "File is too large. Maximum file size is 50MB.",
            ErrorCode.INVALID_FILE_TYPE: "Invalid file type. Please upload a supported file format.",
            ErrorCode.EMPTY_FILE: "The file appears to be empty. Please check your file and try again.",
            ErrorCode.CORRUPTED_FILE: "The file appears to be corrupted. Please try uploading again.",
            
            ErrorCode.UPLOAD_FAILED: "Upload failed. Please try again later.",
            ErrorCode.NETWORK_ERROR: "Network connection issue. Please check your internet connection and try again.",
            ErrorCode.STORAGE_QUOTA_EXCEEDED: "Storage limit reached. Please delete some files or upgrade your plan.",
            ErrorCode.AUTHENTICATION_FAILED: "Authentication failed. Please check your credentials.",
            
            ErrorCode.FILE_NOT_FOUND: "The requested file was not found.",
            ErrorCode.ACCESS_DENIED: "Access to this file is denied.",
            ErrorCode.DOWNLOAD_FAILED: "Download failed. Please try again later.",
            
            ErrorCode.DATABASE_CONNECTION_ERROR: "Database temporarily unavailable. Please try again later.",
            ErrorCode.VALIDATION_ERROR: "Invalid data provided. Please check your input.",
            ErrorCode.DUPLICATE_ENTRY: "An item with this name already exists.",
            
            ErrorCode.INTERNAL_ERROR: "An internal error occurred. Please try again later.",
            ErrorCode.CONFIGURATION_ERROR: "System configuration error. Please contact support.",
            ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests. Please wait a moment and try again."
        }
        
        return user_messages.get(self.error_code, "An unexpected error occurred.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            'error': True,
            'error_code': self.error_code.value,
            'message': self.user_message,
            'details': self.details
        }
    
    def log_error(self):
        """Log the error with appropriate level and details"""
        log_message = f"CloudinaryError [{self.error_code.value}]: {self.message}"
        
        if self.details:
            log_message += f" | Details: {self.details}"
        
        # Log at different levels based on error type
        if self.error_code in [ErrorCode.INTERNAL_ERROR, ErrorCode.CONFIGURATION_ERROR]:
            logger.error(log_message)
        elif self.error_code in [ErrorCode.NETWORK_ERROR, ErrorCode.DATABASE_CONNECTION_ERROR]:
            logger.warning(log_message)
        else:
            logger.info(log_message)


class ErrorHandler:
    """Centralized error handling for Cloudinary operations"""
    
    @staticmethod
    def handle_cloudinary_exception(e: Exception, operation: str = "operation") -> CloudinaryError:
        """
        Convert Cloudinary SDK exceptions to our structured error format
        
        Args:
            e: The original exception
            operation: Description of the operation that failed
            
        Returns:
            CloudinaryError with appropriate error code and message
        """
        
        if isinstance(e, cloudinary.exceptions.Error):
            if "Invalid API key" in str(e) or "Invalid API secret" in str(e):
                return CloudinaryError(
                    message=f"Authentication failed during {operation}: {str(e)}",
                    error_code=ErrorCode.AUTHENTICATION_FAILED,
                    details={'operation': operation, 'original_error': str(e)}
                )
            
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                return CloudinaryError(
                    message=f"Storage quota exceeded during {operation}: {str(e)}",
                    error_code=ErrorCode.STORAGE_QUOTA_EXCEEDED,
                    details={'operation': operation, 'original_error': str(e)}
                )
            
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                return CloudinaryError(
                    message=f"Network error during {operation}: {str(e)}",
                    error_code=ErrorCode.NETWORK_ERROR,
                    details={'operation': operation, 'original_error': str(e)}
                )
            
            elif isinstance(e, cloudinary.exceptions.NotFound):
                return CloudinaryError(
                    message=f"Resource not found during {operation}: {str(e)}",
                    error_code=ErrorCode.FILE_NOT_FOUND,
                    details={'operation': operation, 'original_error': str(e)}
                )
            
            else:
                return CloudinaryError(
                    message=f"Cloudinary error during {operation}: {str(e)}",
                    error_code=ErrorCode.UPLOAD_FAILED,
                    details={'operation': operation, 'original_error': str(e)}
                )
        
        else:
            return CloudinaryError(
                message=f"Unexpected error during {operation}: {str(e)}",
                error_code=ErrorCode.INTERNAL_ERROR,
                details={'operation': operation, 'original_error': str(e)}
            )
    
    @staticmethod
    def validate_file_data(file_data: bytes, filename: str, max_size: int, allowed_types: list) -> Optional[CloudinaryError]:
        """
        Validate file data and return error if validation fails
        
        Args:
            file_data: File bytes to validate
            filename: Original filename
            max_size: Maximum allowed file size in bytes
            allowed_types: List of allowed file extensions
            
        Returns:
            CloudinaryError if validation fails, None if valid
        """
        
        # Check if file is empty
        if not file_data or len(file_data) == 0:
            return CloudinaryError(
                message=f"Empty file: {filename}",
                error_code=ErrorCode.EMPTY_FILE,
                details={'filename': filename, 'size': len(file_data)}
            )
        
        # Check file size
        if len(file_data) > max_size:
            return CloudinaryError(
                message=f"File too large: {filename} ({len(file_data)} bytes > {max_size} bytes)",
                error_code=ErrorCode.FILE_TOO_LARGE,
                details={
                    'filename': filename, 
                    'file_size': len(file_data), 
                    'max_size': max_size,
                    'max_size_mb': max_size // (1024 * 1024)
                }
            )
        
        # Check file extension
        import os
        file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if file_extension not in allowed_types:
            return CloudinaryError(
                message=f"Invalid file type: {filename} (.{file_extension})",
                error_code=ErrorCode.INVALID_FILE_TYPE,
                details={
                    'filename': filename,
                    'file_extension': file_extension,
                    'allowed_types': allowed_types
                }
            )
        
        return None
    
    @staticmethod
    def create_success_response(data: Dict[str, Any], message: str = "Operation successful") -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Standardized success response dictionary
        """
        return {
            'success': True,
            'message': message,
            'data': data,
            'error': False
        }
    
    @staticmethod
    def handle_operation(operation_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Wrapper to handle any operation with standardized error handling
        
        Args:
            operation_func: Function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Standardized response dictionary
        """
        try:
            result = operation_func(*args, **kwargs)
            return ErrorHandler.create_success_response(result)
            
        except CloudinaryError as e:
            e.log_error()
            return e.to_dict()
            
        except Exception as e:
            error = ErrorHandler.handle_cloudinary_exception(e, "operation")
            error.log_error()
            return error.to_dict()


# Utility functions for common operations
def safe_upload_model(upload_func, file_data, filename, user_id, model_name):
    """Safely upload a model with error handling"""
    return ErrorHandler.handle_operation(
        upload_func, file_data, filename, user_id, model_name
    )


def safe_upload_simulation(upload_func, file_data, filename, user_id, simulation_name, file_type='html'):
    """Safely upload a simulation with error handling"""
    return ErrorHandler.handle_operation(
        upload_func, file_data, filename, user_id, simulation_name, file_type
    )


def safe_delete_file(delete_func, public_id):
    """Safely delete a file with error handling"""
    return ErrorHandler.handle_operation(delete_func, public_id)


def safe_get_download_url(url_func, public_id, expiration=3600):
    """Safely get download URL with error handling"""
    return ErrorHandler.handle_operation(url_func, public_id, expiration)


# Export main classes and functions
__all__ = [
    'CloudinaryError',
    'ErrorCode',
    'ErrorHandler',
    'safe_upload_model',
    'safe_upload_simulation',
    'safe_delete_file',
    'safe_get_download_url'
]