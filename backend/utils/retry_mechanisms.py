"""
Retry Mechanisms for Network Operations and External API Calls
Provides robust retry logic with exponential backoff for improved reliability
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Optional, Union, List, Type
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout
import cloudinary.exceptions
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        backoff_factor: float = 0.1
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.backoff_factor = backoff_factor


class RetryableError(Exception):
    """Base class for errors that should trigger retry"""
    pass


class NonRetryableError(Exception):
    """Base class for errors that should NOT trigger retry"""
    pass


# Define which exceptions are retryable for different operations
DATABASE_RETRYABLE_EXCEPTIONS = (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    NetworkTimeout,
    OSError  # Network-level issues
)

CLOUDINARY_RETRYABLE_EXCEPTIONS = (
    cloudinary.exceptions.Error,
    ConnectionError,
    Timeout,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout
)

NETWORK_RETRYABLE_EXCEPTIONS = (
    RequestException,
    ConnectionError,
    Timeout,
    OSError
)


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """
    Calculate delay for retry attempt using exponential backoff with jitter
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
    
    Returns:
        Delay in seconds
    """
    # Exponential backoff
    delay = config.base_delay * (config.exponential_base ** attempt)
    
    # Cap at maximum delay
    delay = min(delay, config.max_delay)
    
    # Add jitter to prevent thundering herd
    if config.jitter:
        jitter_amount = delay * config.backoff_factor
        jitter = random.uniform(-jitter_amount, jitter_amount)
        delay = max(0, delay + jitter)
    
    return delay


def retry_operation(
    config: RetryConfig,
    retryable_exceptions: tuple,
    operation_name: str = "operation"
):
    """
    Decorator for retrying operations with exponential backoff
    
    Args:
        config: Retry configuration
        retryable_exceptions: Tuple of exception types that should trigger retry
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    logger.debug(f"Attempting {operation_name} (attempt {attempt + 1}/{config.max_attempts})")
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"{operation_name} succeeded after {attempt + 1} attempts")
                    
                    return result
                
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            f"{operation_name} failed (attempt {attempt + 1}/{config.max_attempts}): {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{operation_name} failed after {config.max_attempts} attempts: {str(e)}"
                        )
                
                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"{operation_name} failed with non-retryable error: {str(e)}")
                    raise
            
            # If we reach here, all attempts failed
            raise RetryableError(f"{operation_name} failed after {config.max_attempts} attempts") from last_exception
        
        return wrapper
    return decorator


# Pre-configured retry decorators for common operations
def retry_database_operation(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0
):
    """Retry decorator for database operations"""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=2.0,
        jitter=True
    )
    return retry_operation(config, DATABASE_RETRYABLE_EXCEPTIONS, "database operation")


def retry_cloudinary_operation(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0
):
    """Retry decorator for Cloudinary operations"""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=2.0,
        jitter=True
    )
    return retry_operation(config, CLOUDINARY_RETRYABLE_EXCEPTIONS, "cloudinary operation")


def retry_network_operation(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Retry decorator for network operations"""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=2.0,
        jitter=True
    )
    return retry_operation(config, NETWORK_RETRYABLE_EXCEPTIONS, "network operation")


class RetryableOperationManager:
    """
    Manager class for executing retryable operations with context
    """
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute_with_retry(
        self,
        operation: Callable,
        retryable_exceptions: tuple,
        operation_name: str = "operation",
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an operation with retry logic
        
        Args:
            operation: Function to execute
            retryable_exceptions: Exceptions that should trigger retry
            operation_name: Name for logging
            *args, **kwargs: Arguments to pass to the operation
        
        Returns:
            Result of the operation
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                logger.debug(f"Executing {operation_name} (attempt {attempt + 1}/{self.config.max_attempts})")
                result = operation(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt + 1} attempts")
                
                return result
            
            except retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.config.max_attempts - 1:
                    delay = calculate_delay(attempt, self.config)
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.config.max_attempts}): {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"{operation_name} failed after {self.config.max_attempts} attempts: {str(e)}"
                    )
            
            except Exception as e:
                logger.error(f"{operation_name} failed with non-retryable error: {str(e)}")
                raise
        
        raise RetryableError(f"{operation_name} failed after {self.config.max_attempts} attempts") from last_exception


# Circuit breaker pattern for preventing cascade failures
class CircuitBreaker:
    """
    Circuit breaker to prevent cascade failures when external services are down
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit breaker moving to HALF_OPEN state for {func.__name__}")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN for {func.__name__}. "
                        f"Try again in {self.recovery_timeout} seconds."
                    )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation"""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker reset to CLOSED state")
        
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Pre-configured circuit breakers for common services
database_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
    expected_exception=Exception
)

cloudinary_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=60.0,
    expected_exception=Exception
)


# Utility functions for common retry patterns
def with_database_retry(func: Callable) -> Callable:
    """Apply database retry logic to a function"""
    return retry_database_operation()(func)


def with_cloudinary_retry(func: Callable) -> Callable:
    """Apply Cloudinary retry logic to a function"""
    return retry_cloudinary_operation()(func)


def with_network_retry(func: Callable) -> Callable:
    """Apply network retry logic to a function"""
    return retry_network_operation()(func)


# Example usage functions for testing retry mechanisms
@retry_database_operation(max_attempts=3)
def test_database_connection():
    """Test function for database retry mechanism"""
    from utils.database import get_database
    db = get_database()
    return db.command('ping')


@retry_cloudinary_operation(max_attempts=3)
def test_cloudinary_connection():
    """Test function for Cloudinary retry mechanism"""
    import cloudinary.api
    return cloudinary.api.ping()


def create_retry_manager(operation_type: str) -> RetryableOperationManager:
    """
    Create a retry manager for specific operation types
    
    Args:
        operation_type: Type of operation ('database', 'cloudinary', 'network')
    
    Returns:
        Configured RetryableOperationManager
    """
    configs = {
        'database': RetryConfig(max_attempts=3, base_delay=0.5, max_delay=10.0),
        'cloudinary': RetryConfig(max_attempts=3, base_delay=1.0, max_delay=30.0),
        'network': RetryConfig(max_attempts=3, base_delay=1.0, max_delay=60.0),
        'default': RetryConfig(max_attempts=3, base_delay=1.0, max_delay=30.0)
    }
    
    config = configs.get(operation_type, configs['default'])
    return RetryableOperationManager(config)