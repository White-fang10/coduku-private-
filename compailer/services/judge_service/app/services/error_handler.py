"""
Comprehensive error handling and recovery for Judge Service
"""
import logging
import asyncio
from enum import Enum
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)


class ErrorCategory(str, Enum):
    """Error categorization for handling strategies"""
    JUDGE0_OFFLINE = "judge0_offline"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"
    WRONG_ANSWER = "wrong_answer"
    INVALID_LANGUAGE = "invalid_language"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Centralized error handling with recovery strategies"""
    
    # Error patterns for categorization
    ERROR_PATTERNS = {
        ErrorCategory.JUDGE0_OFFLINE: [
            "connection refused", "unreachable", "offline", "503", "504",
            "cannot connect", "connection error", "judge0 error"
        ],
        ErrorCategory.TIMEOUT: [
            "timeout", "timed out", "time limit", "exceeded", "took too long"
        ],
        ErrorCategory.MEMORY_ERROR: [
            "memory", "oom", "out of memory", "memory limit"
        ],
        ErrorCategory.COMPILATION_ERROR: [
            "compilation", "syntax", "compile error", "compilation error"
        ],
        ErrorCategory.RUNTIME_ERROR: [
            "runtime", "segmentation fault", "access violation", "undefined",
            "division by zero", "null pointer", "exception"
        ],
        ErrorCategory.INVALID_LANGUAGE: [
            "unsupported language", "language not supported"
        ]
    }
    
    @staticmethod
    def categorize(error_message: str) -> Dict[str, Any]:
        """
        Categorize an error and determine recovery strategy
        
        Returns:
            {
                "category": ErrorCategory,
                "user_message": str,
                "recoverable": bool,
                "should_retry": bool,
                "max_retries": int,
                "retry_delay": float,
                "details": str
            }
        """
        error_lower = error_message.lower()
        
        # Check each category
        for category, patterns in ErrorHandler.ERROR_PATTERNS.items():
            if any(pattern in error_lower for pattern in patterns):
                return ErrorHandler._get_recovery_strategy(category, error_message)
        
        # Default to unknown
        return ErrorHandler._get_recovery_strategy(ErrorCategory.UNKNOWN, error_message)
    
    @staticmethod
    def _get_recovery_strategy(category: ErrorCategory, details: str) -> Dict[str, Any]:
        """Get recovery strategy for an error category"""
        
        strategies = {
            ErrorCategory.JUDGE0_OFFLINE: {
                "user_message": "Compiler service temporarily unavailable. Please try again in a moment.",
                "recoverable": True,
                "should_retry": True,
                "max_retries": 5,
                "retry_delay": 2.0,  # Start with 2 second delay
            },
            ErrorCategory.TIMEOUT: {
                "user_message": "Code execution took too long. Your code might have an infinite loop or be inefficient.",
                "recoverable": True,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.MEMORY_ERROR: {
                "user_message": "Code used too much memory. Optimize your data structures or reduce input size.",
                "recoverable": True,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.COMPILATION_ERROR: {
                "user_message": "Syntax error in your code. Check the error details below.",
                "recoverable": True,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.RUNTIME_ERROR: {
                "user_message": "Runtime error in your code. Check for null pointers, array bounds, or invalid operations.",
                "recoverable": True,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.WRONG_ANSWER: {
                "user_message": "Your output doesn't match the expected output for this test case.",
                "recoverable": True,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.INVALID_LANGUAGE: {
                "user_message": "Programming language not supported. Please choose from the available languages.",
                "recoverable": False,
                "should_retry": False,
                "max_retries": 0,
                "retry_delay": 0,
            },
            ErrorCategory.UNKNOWN: {
                "user_message": "An unexpected error occurred. Please try again or contact support.",
                "recoverable": True,
                "should_retry": True,
                "max_retries": 3,
                "retry_delay": 1.0,
            }
        }
        
        strategy = strategies.get(category, strategies[ErrorCategory.UNKNOWN])
        
        return {
            "category": category.value,
            **strategy,
            "details": details
        }
    
    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Retry a coroutine function with exponential backoff
        
        Args:
            func: Async function to call (no parameters)
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay cap
            backoff_factor: Exponential backoff multiplier
        
        Returns:
            Result from successful call
        
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        delay = initial_delay
        
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    logger.warning(
                        f"⚠️Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                else:
                    logger.error(f"❌ All {max_retries + 1} attempts failed")
        
        raise last_exception
    
    @staticmethod
    async def handle_gracefully(
        func: Callable,
        error_callback: Callable = None,
        timeout: float = 30.0
    ) -> tuple[bool, Any]:
        """
        Execute function with comprehensive error handling
        
        Returns:
            (success: bool, result_or_error: Any)
        """
        try:
            result = await asyncio.wait_for(func(), timeout=timeout)
            return True, result
        except asyncio.TimeoutError:
            error_info = ErrorHandler.categorize("Execution timeout")
            if error_callback:
                await error_callback(error_info)
            return False, error_info
        except Exception as e:
            error_info = ErrorHandler.categorize(str(e))
            if error_callback:
                await error_callback(error_info)
            return False, error_info
    
    @staticmethod
    def format_error_for_display(error_message: str, max_length: int = 500) -> str:
        """Format error message for frontend display"""
        if not error_message:
            return "(no error details)"
        
        # Truncate if too long
        if len(error_message) > max_length:
            error_message = error_message[:max_length] + "\n... (truncated)"
        
        # Clean up markup
        error_message = error_message.strip()
        
        return error_message


# Circuit breaker pattern for external services
class CircuitBreaker:
    """Simple circuit breaker for Judge0 service"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    async def call(self, func: Callable) -> Any:
        """Execute function through circuit breaker"""
        
        # Check if circuit is open and should reset
        if self.is_open:
            import time
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("🔄 Circuit breaker: attempting reset...")
                self.is_open = False
                self.failure_count = 0
            else:
                raise RuntimeError("Circuit breaker is OPEN - service temporarily unavailable")
        
        try:
            result = await func()
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            import time
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(f"🔴 Circuit breaker OPENED after {self.failure_count} failures")
            
            raise
    
    def status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        import time
        
        return {
            "is_open": self.is_open,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout_seconds": self.timeout,
            "last_failure": self.last_failure_time,
            "time_to_reset": max(0, self.timeout - (time.time() - self.last_failure_time)) if self.last_failure_time else None
        }


# Create global circuit breaker for Judge0
judge0_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
