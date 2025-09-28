"""
Comprehensive Input Validation and Security Middleware
Provides data sanitization, validation, and security checks for all API endpoints
"""

import re
import html
import json
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from flask import request, jsonify, g
from werkzeug.datastructures import FileStorage
import logging
import secrets
import hashlib
from datetime import datetime
from pymongo.objectid import ObjectId
import bleach

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class InputValidator:
    """
    Comprehensive input validation and sanitization
    """
    
    # Security patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b.*\b=\b|\bAND\b.*\b=\b)",
        r"(\bxp_cmdshell\b|\bsp_executesql\b)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed"
    ]
    
    # Safe HTML tags for rich text (if needed)
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_HTML_ATTRIBUTES = {}
    
    @staticmethod
    def validate_string(
        value: Any,
        field_name: str,
        min_length: int = 0,
        max_length: int = 1000,
        pattern: Optional[str] = None,
        required: bool = True,
        sanitize: bool = True
    ) -> str:
        """
        Validate and sanitize string input
        
        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            pattern: Optional regex pattern to match
            required: Whether the field is required
            sanitize: Whether to sanitize the input
            
        Returns:
            Validated and sanitized string
        """
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return ""
        
        if not isinstance(value, str):
            if isinstance(value, (int, float)):
                value = str(value)
            else:
                raise ValidationError(f"{field_name} must be a string")
        
        # Basic sanitization
        if sanitize:
            value = value.strip()
            value = html.escape(value)  # Escape HTML entities
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must be at most {max_length} characters long")
        
        # Pattern validation
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"{field_name} format is invalid")
        
        # Security checks
        InputValidator._check_security_patterns(value, field_name)
        
        return value
    
    @staticmethod
    def validate_email(email: str, required: bool = True) -> str:
        """Validate email format"""
        if not email and not required:
            return ""
        
        email = InputValidator.validate_string(
            email, "email", min_length=1, max_length=255, required=required
        )
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        return email.lower()  # Normalize to lowercase
    
    @staticmethod
    def validate_integer(
        value: Any,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        required: bool = True
    ) -> int:
        """Validate integer input"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return 0
        
        try:
            if isinstance(value, str):
                value = int(value)
            elif not isinstance(value, int):
                raise ValueError()
        except ValueError:
            raise ValidationError(f"{field_name} must be an integer")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be at most {max_value}")
        
        return value
    
    @staticmethod
    def validate_float(
        value: Any,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        required: bool = True
    ) -> float:
        """Validate float input"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return 0.0
        
        try:
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                raise ValueError()
        except ValueError:
            raise ValidationError(f"{field_name} must be a number")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be at most {max_value}")
        
        return float(value)
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str, required: bool = True) -> bool:
        """Validate boolean input"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
        
        if isinstance(value, int):
            return bool(value)
        
        raise ValidationError(f"{field_name} must be a boolean value")
    
    @staticmethod
    def validate_list(
        value: Any,
        field_name: str,
        min_items: int = 0,
        max_items: int = 100,
        item_type: type = str,
        required: bool = True
    ) -> list:
        """Validate list input"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return []
        
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        
        if len(value) < min_items:
            raise ValidationError(f"{field_name} must have at least {min_items} items")
        
        if len(value) > max_items:
            raise ValidationError(f"{field_name} must have at most {max_items} items")
        
        # Validate each item
        validated_items = []
        for i, item in enumerate(value):
            if not isinstance(item, item_type):
                if item_type == str and isinstance(item, (int, float)):
                    item = str(item)
                else:
                    raise ValidationError(f"{field_name}[{i}] must be of type {item_type.__name__}")
            
            if item_type == str:
                item = InputValidator.validate_string(item, f"{field_name}[{i}]", max_length=100)
            
            validated_items.append(item)
        
        return validated_items
    
    @staticmethod
    def validate_json(value: Any, field_name: str, required: bool = True) -> dict:
        """Validate JSON input"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return {}
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(f"{field_name} must be valid JSON")
        
        raise ValidationError(f"{field_name} must be a JSON object")
    
    @staticmethod
    def validate_object_id(value: Any, field_name: str, required: bool = True) -> str:
        """Validate MongoDB ObjectId"""
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required")
            return ""
        
        if isinstance(value, ObjectId):
            return str(value)
        
        if isinstance(value, str):
            try:
                ObjectId(value)
                return value
            except:
                raise ValidationError(f"{field_name} must be a valid ObjectId")
        
        raise ValidationError(f"{field_name} must be a valid ObjectId")
    
    @staticmethod
    def validate_file(
        file: FileStorage,
        field_name: str,
        allowed_extensions: List[str],
        max_size: int = 50 * 1024 * 1024,  # 50MB
        required: bool = True
    ) -> FileStorage:
        """Validate file upload"""
        if not file or not file.filename:
            if required:
                raise ValidationError(f"{field_name} is required")
            return None
        
        # Check filename
        if not InputValidator._is_safe_filename(file.filename):
            raise ValidationError(f"{field_name} has unsafe filename")
        
        # Check extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in [ext.lower() for ext in allowed_extensions]:
            raise ValidationError(
                f"{field_name} must be one of: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset position
        
        if size > max_size:
            max_size_mb = max_size // (1024 * 1024)
            raise ValidationError(f"{field_name} must be smaller than {max_size_mb}MB")
        
        if size == 0:
            raise ValidationError(f"{field_name} cannot be empty")
        
        return file
    
    @staticmethod
    def _check_security_patterns(value: str, field_name: str):
        """Check for common security attack patterns"""
        # Check for SQL injection patterns
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected in {field_name}: {value}")
                raise SecurityError(f"Invalid characters detected in {field_name}")
        
        # Check for XSS patterns
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential XSS detected in {field_name}: {value}")
                raise SecurityError(f"Invalid content detected in {field_name}")
    
    @staticmethod
    def _is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        # Basic filename validation
        if not filename or filename in ['.', '..']:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        # Check length
        if len(filename) > 255:
            return False
        
        return True
    
    @staticmethod
    def sanitize_html(content: str) -> str:
        """Sanitize HTML content while preserving safe tags"""
        return bleach.clean(
            content,
            tags=InputValidator.ALLOWED_HTML_TAGS,
            attributes=InputValidator.ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )


class RateLimiter:
    """
    Simple rate limiting functionality
    """
    
    def __init__(self):
        self.requests = {}  # {client_id: [(timestamp, endpoint), ...]}
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = datetime.now()
    
    def is_allowed(
        self,
        client_id: str,
        endpoint: str,
        limit: int = 100,
        window: int = 3600  # 1 hour
    ) -> bool:
        """
        Check if request is allowed based on rate limiting
        
        Args:
            client_id: Unique identifier for the client
            endpoint: API endpoint being accessed
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.now()
        
        # Cleanup old entries periodically
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup_old_entries(now, window)
            self.last_cleanup = now
        
        # Get client's request history
        client_requests = self.requests.get(client_id, [])
        
        # Filter requests within the time window for this endpoint
        recent_requests = [
            req_time for req_time, req_endpoint in client_requests
            if (now - req_time).total_seconds() < window and req_endpoint == endpoint
        ]
        
        # Check if limit is exceeded
        if len(recent_requests) >= limit:
            return False
        
        # Add current request
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id].append((now, endpoint))
        
        return True
    
    def _cleanup_old_entries(self, now: datetime, window: int):
        """Clean up old request entries"""
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                (req_time, endpoint) for req_time, endpoint in self.requests[client_id]
                if (now - req_time).total_seconds() < window * 2  # Keep some history
            ]
            
            # Remove clients with no recent requests
            if not self.requests[client_id]:
                del self.requests[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter()


def validate_request(validation_rules: Dict[str, Dict[str, Any]]):
    """
    Decorator for request validation
    
    Args:
        validation_rules: Dictionary of field validation rules
        Example:
        {
            'model_name': {'type': 'string', 'required': True, 'max_length': 100},
            'model_type': {'type': 'string', 'required': True, 'pattern': r'^(regression|classification)$'},
            'training_time': {'type': 'float', 'required': True, 'min_value': 0}
        }
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Rate limiting
                client_id = request.remote_addr
                endpoint = request.endpoint or f.__name__
                
                if not rate_limiter.is_allowed(client_id, endpoint):
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'RATE_LIMIT_EXCEEDED',
                            'message': 'Too many requests. Please try again later.'
                        }
                    }), 429
                
                # Validate request data
                validated_data = {}
                
                # Get data from different sources based on request type
                if request.is_json:
                    request_data = request.get_json() or {}
                else:
                    request_data = request.form.to_dict()
                
                # Add files if present
                if request.files:
                    for key, file in request.files.items():
                        request_data[key] = file
                
                # Validate each field
                for field_name, rules in validation_rules.items():
                    value = request_data.get(field_name)
                    field_type = rules.get('type', 'string')
                    required = rules.get('required', False)
                    
                    if field_type == 'string':
                        validated_data[field_name] = InputValidator.validate_string(
                            value, field_name,
                            min_length=rules.get('min_length', 0),
                            max_length=rules.get('max_length', 1000),
                            pattern=rules.get('pattern'),
                            required=required
                        )
                    
                    elif field_type == 'integer':
                        validated_data[field_name] = InputValidator.validate_integer(
                            value, field_name,
                            min_value=rules.get('min_value'),
                            max_value=rules.get('max_value'),
                            required=required
                        )
                    
                    elif field_type == 'float':
                        validated_data[field_name] = InputValidator.validate_float(
                            value, field_name,
                            min_value=rules.get('min_value'),
                            max_value=rules.get('max_value'),
                            required=required
                        )
                    
                    elif field_type == 'boolean':
                        validated_data[field_name] = InputValidator.validate_boolean(
                            value, field_name, required=required
                        )
                    
                    elif field_type == 'list':
                        validated_data[field_name] = InputValidator.validate_list(
                            value, field_name,
                            min_items=rules.get('min_items', 0),
                            max_items=rules.get('max_items', 100),
                            item_type=rules.get('item_type', str),
                            required=required
                        )
                    
                    elif field_type == 'json':
                        validated_data[field_name] = InputValidator.validate_json(
                            value, field_name, required=required
                        )
                    
                    elif field_type == 'email':
                        validated_data[field_name] = InputValidator.validate_email(
                            value, required=required
                        )
                    
                    elif field_type == 'objectid':
                        validated_data[field_name] = InputValidator.validate_object_id(
                            value, field_name, required=required
                        )
                    
                    elif field_type == 'file':
                        validated_data[field_name] = InputValidator.validate_file(
                            value, field_name,
                            allowed_extensions=rules.get('allowed_extensions', []),
                            max_size=rules.get('max_size', 50 * 1024 * 1024),
                            required=required
                        )
                
                # Store validated data in request context
                g.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except (ValidationError, SecurityError) as e:
                logger.warning(f"Validation error in {endpoint}: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': str(e)
                    }
                }), 400
            
            except Exception as e:
                logger.error(f"Unexpected error in validation: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INTERNAL_ERROR',
                        'message': 'An unexpected error occurred during validation'
                    }
                }), 500
        
        return decorated_function
    return decorator


def get_validated_data() -> Dict[str, Any]:
    """Get validated data from request context"""
    return getattr(g, 'validated_data', {})