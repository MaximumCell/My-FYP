"""
Comprehensive Error Handling Middleware for PhysicsLab Application
Provides centralized error handling, logging, and standardized responses
"""

import logging
import traceback
from functools import wraps
from flask import request, jsonify, g
from typing import Dict, Any, Optional, Callable
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge
from .error_handler import ErrorCode, CloudinaryErrorHandler
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorTracker:
    """Track error patterns and frequencies for monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_reset = time.time()
        self.reset_interval = 3600  # Reset counts every hour
    
    def track_error(self, error_type: str, endpoint: str):
        """Track error occurrence"""
        current_time = time.time()
        
        # Reset counts if interval has passed
        if current_time - self.last_reset > self.reset_interval:
            self.error_counts = {}
            self.last_reset = current_time
        
        key = f"{error_type}:{endpoint}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Log if error frequency is high
        if self.error_counts[key] > 10:  # More than 10 errors per hour
            logger.error(f"High error frequency detected: {key} - {self.error_counts[key]} errors")
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get current error statistics"""
        return self.error_counts.copy()


# Global error tracker instance
error_tracker = ErrorTracker()


def handle_errors(f):
    """
    Decorator for comprehensive error handling in Flask routes
    Automatically catches and handles various types of errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Set request context
            g.start_time = start_time
            g.endpoint = request.endpoint or f.__name__
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log successful requests (debug level)
            duration = time.time() - start_time
            logger.debug(f"Request completed: {g.endpoint} - {duration:.3f}s")
            
            return result
            
        except ValueError as e:
            return _handle_validation_error(str(e))
            
        except PyMongoError as e:
            return _handle_database_error(e)
            
        except ConnectionFailure as e:
            return _handle_connection_error(e)
            
        except RequestEntityTooLarge as e:
            return _handle_file_size_error(e)
            
        except HTTPException as e:
            return _handle_http_error(e)
            
        except Exception as e:
            return _handle_generic_error(e)
    
    return decorated_function


def _handle_validation_error(error_message: str) -> tuple:
    """Handle validation errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('validation', endpoint)
    
    logger.warning(f"Validation error in {endpoint}: {error_message}")
    
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.VALIDATION_ERROR,
        "Invalid input data. Please check your request and try again.",
        error_message
    ), 400


def _handle_database_error(error: PyMongoError) -> tuple:
    """Handle database-related errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('database', endpoint)
    
    error_message = str(error)
    
    if isinstance(error, ServerSelectionTimeoutError):
        logger.error(f"Database connection timeout in {endpoint}: {error_message}")
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.DB_CONNECTION_ERROR,
            "Database is temporarily unavailable. Please try again later.",
            error_message
        ), 503
    
    elif isinstance(error, ConnectionFailure):
        logger.error(f"Database connection failed in {endpoint}: {error_message}")
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.DB_CONNECTION_ERROR,
            "Unable to connect to database. Please try again later.",
            error_message
        ), 503
    
    elif "duplicate key" in error_message.lower():
        logger.warning(f"Duplicate entry attempt in {endpoint}: {error_message}")
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.DUPLICATE_ENTRY,
            "An item with this name already exists. Please choose a different name.",
            error_message
        ), 409
    
    else:
        logger.error(f"Database error in {endpoint}: {error_message}")
        return CloudinaryErrorHandler.format_error_response(
            ErrorCode.INTERNAL_ERROR,
            "A database error occurred. Please try again later.",
            error_message
        ), 500


def _handle_connection_error(error: Exception) -> tuple:
    """Handle network/connection errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('connection', endpoint)
    
    logger.error(f"Connection error in {endpoint}: {str(error)}")
    
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.NETWORK_ERROR,
        "Network connection issue. Please check your internet connection and try again.",
        str(error)
    ), 503


def _handle_file_size_error(error: RequestEntityTooLarge) -> tuple:
    """Handle file size limit exceeded errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('file_size', endpoint)
    
    logger.warning(f"File size exceeded in {endpoint}: {str(error)}")
    
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.FILE_TOO_LARGE,
        "File size exceeds the maximum allowed limit of 50MB. Please compress your file or use a smaller dataset.",
        str(error)
    ), 413


def _handle_http_error(error: HTTPException) -> tuple:
    """Handle HTTP-specific errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('http', endpoint)
    
    logger.warning(f"HTTP error {error.code} in {endpoint}: {error.description}")
    
    # Map HTTP status codes to our error codes
    if error.code == 404:
        error_code = ErrorCode.FILE_NOT_FOUND
        message = "Requested resource not found."
    elif error.code == 401:
        error_code = ErrorCode.AUTHENTICATION_ERROR
        message = "Authentication required."
    elif error.code == 403:
        error_code = ErrorCode.ACCESS_DENIED
        message = "Access to this resource is denied."
    elif error.code == 413:
        error_code = ErrorCode.FILE_TOO_LARGE
        message = "Request payload too large."
    elif error.code == 415:
        error_code = ErrorCode.INVALID_FILE_TYPE
        message = "Unsupported media type."
    elif error.code == 429:
        error_code = ErrorCode.QUOTA_EXCEEDED
        message = "Too many requests. Please try again later."
    else:
        error_code = ErrorCode.INTERNAL_ERROR
        message = "An error occurred while processing your request."
    
    return CloudinaryErrorHandler.format_error_response(
        error_code,
        message,
        error.description
    ), error.code


def _handle_generic_error(error: Exception) -> tuple:
    """Handle unexpected errors"""
    endpoint = getattr(g, 'endpoint', 'unknown')
    error_tracker.track_error('generic', endpoint)
    
    # Get detailed error information
    error_message = str(error)
    error_type = type(error).__name__
    
    # Log the full traceback for debugging
    tb = traceback.format_exc()
    logger.error(f"Unexpected error in {endpoint}: {error_type}: {error_message}")
    logger.error(f"Traceback: {tb}")
    
    # Don't expose internal error details to users in production
    user_message = "An unexpected error occurred. Please try again later."
    
    return CloudinaryErrorHandler.format_error_response(
        ErrorCode.INTERNAL_ERROR,
        user_message,
        error_message if logger.level <= logging.DEBUG else None
    ), 500


class RequestValidator:
    """Validate and sanitize incoming requests"""
    
    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validate and sanitize user ID"""
        if not user_id:
            raise ValueError("User ID is required")
        
        # Basic sanitization
        user_id = user_id.strip()
        
        if len(user_id) < 1 or len(user_id) > 100:
            raise ValueError("Invalid user ID format")
        
        # Check for MongoDB ObjectId format if applicable
        if len(user_id) == 24:
            try:
                int(user_id, 16)  # Valid hex string
            except ValueError:
                raise ValueError("Invalid user ID format")
        
        return user_id
    
    @staticmethod
    def validate_model_name(name: str) -> str:
        """Validate and sanitize model name"""
        if not name:
            raise ValueError("Model name is required")
        
        name = name.strip()
        
        if len(name) < 1 or len(name) > 100:
            raise ValueError("Model name must be between 1 and 100 characters")
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '/', '\\', '|']
        for char in dangerous_chars:
            name = name.replace(char, '')
        
        if not name:
            raise ValueError("Model name contains only invalid characters")
        
        return name
    
    @staticmethod
    def validate_pagination(page: Optional[str], page_size: Optional[str]) -> tuple:
        """Validate pagination parameters"""
        try:
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 10
        except ValueError:
            raise ValueError("Page and page_size must be integers")
        
        if page < 1:
            page = 1
        
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        return page, page_size
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: list = None) -> dict:
        """Validate JSON request data"""
        if not isinstance(data, dict):
            raise ValueError("Request body must be valid JSON object")
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return data


def log_request_info():
    """Log request information for debugging"""
    if logger.level <= logging.DEBUG:
        logger.debug(f"Request: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        if request.is_json:
            try:
                json_body = request.get_json(silent=True)
                if json_body is not None:
                    logger.debug(f"JSON body: {json_body}")
            except Exception as e:
                logger.debug(f"Could not parse JSON body: {str(e)}")


def setup_error_handlers(app):
    """Setup global error handlers for Flask app"""
    
    @app.before_request
    def before_request():
        """Log request information and setup request context"""
        log_request_info()
        g.start_time = time.time()
        g.endpoint = request.endpoint
    
    @app.after_request
    def after_request(response):
        """Log response information"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        return response
    
    @app.errorhandler(400)
    def handle_400(error):
        return _handle_http_error(error)
    
    @app.errorhandler(401)
    def handle_401(error):
        return _handle_http_error(error)
    
    @app.errorhandler(403)
    def handle_403(error):
        return _handle_http_error(error)
    
    @app.errorhandler(404)
    def handle_404(error):
        return _handle_http_error(error)
    
    @app.errorhandler(413)
    def handle_413(error):
        return _handle_file_size_error(error)
    
    @app.errorhandler(415)
    def handle_415(error):
        return _handle_http_error(error)
    
    @app.errorhandler(429)
    def handle_429(error):
        return _handle_http_error(error)
    
    @app.errorhandler(500)
    def handle_500(error):
        return _handle_generic_error(error)
    
    @app.errorhandler(503)
    def handle_503(error):
        return _handle_connection_error(error)


def get_error_stats() -> Dict[str, Any]:
    """Get current error statistics for monitoring"""
    return {
        'error_counts': error_tracker.get_error_stats(),
        'last_reset': error_tracker.last_reset,
        'reset_interval': error_tracker.reset_interval
    }