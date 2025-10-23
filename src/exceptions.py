"""Custom exceptions for ABP Agent."""
from typing import Dict, Any, Optional


class ABPException(Exception):
    """Base exception for ABP Agent."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class CalendarAPIError(ABPException):
    """Calendar API operation failed."""
    pass


class AuthenticationError(ABPException):
    """OAuth/credentials error."""
    pass


class ConstitutionViolation(ABPException):
    """Meeting violates user's constitution."""
    pass


class LLMError(ABPException):
    """LLM API error."""
    pass


class ReschedulingError(ABPException):
    """Rescheduling operation failed."""
    pass


class EmailServiceError(ABPException):
    """Email operation failed."""
    pass
