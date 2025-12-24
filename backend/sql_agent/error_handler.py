"""
Enhanced error handling with Context7 integration for better error messages.
"""
from typing import Dict, Optional
from .everflow_api_validator import get_validator
import logging

logger = logging.getLogger(__name__)


class EverflowErrorHandler:
    """Enhanced error handler with Context7 integration."""
    
    def __init__(self):
        self.validator = get_validator()
    
    def handle_api_error(
        self,
        error: Exception,
        endpoint: str,
        method: str = "POST",
        payload: Optional[Dict] = None
    ) -> str:
        """
        Generate user-friendly error message with Context7 suggestions.
        
        Args:
            error: The exception that occurred
            endpoint: API endpoint that failed
            method: HTTP method used
            payload: Request payload (if any)
        
        Returns:
            User-friendly error message
        """
        error_msg = str(error)
        
        # Check if it's a validation error
        if "Validation Failed" in error_msg:
            return self._format_validation_error(error_msg)
        
        # Check if it's an HTTP error
        if hasattr(error, 'response') and error.response is not None:
            status_code = getattr(error.response, 'status_code', None)
            return self._format_http_error(status_code, endpoint, method, payload)
        
        # Generic error
        return self._format_generic_error(error_msg, endpoint)
    
    def _format_validation_error(self, error_msg: str) -> str:
        """Format validation error message."""
        lines = ["❌ API Request Validation Failed"]
        lines.append("")
        
        # Extract errors and suggestions
        if "Errors:" in error_msg:
            lines.append("**Errors:**")
            # Parse and format errors
            # (Simplified - in production, parse the structured error)
            lines.append(error_msg)
        
        return "\n".join(lines)
    
    def _format_http_error(
        self,
        status_code: int,
        endpoint: str,
        method: str,
        payload: Optional[Dict]
    ) -> str:
        """Format HTTP error with Context7 suggestions."""
        lines = [f"❌ API Error (Status {status_code})"]
        lines.append("")
        
        # Map status codes to helpful messages
        status_messages = {
            400: "Bad Request - The request parameters are invalid.",
            401: "Unauthorized - Check your API key.",
            403: "Forbidden - You don't have permission to access this endpoint.",
            404: "Not Found - The endpoint or resource doesn't exist.",
            429: "Rate Limit Exceeded - Please wait before making more requests.",
            500: "Internal Server Error - The Everflow API encountered an error.",
            502: "Bad Gateway - The Everflow API is temporarily unavailable.",
            503: "Service Unavailable - The Everflow API is down for maintenance.",
        }
        
        if status_code in status_messages:
            lines.append(status_messages[status_code])
        else:
            lines.append(f"Unexpected error (Status {status_code})")
        
        lines.append("")
        lines.append(f"**Endpoint:** {method} {endpoint}")
        
        # Get suggestions from validator
        if status_code == 404:
            suggestion = self.validator.get_endpoint_suggestion(f"operation on {endpoint}")
            if suggestion and suggestion != endpoint:
                lines.append("")
                lines.append(f"💡 **Suggestion:** Did you mean `{suggestion}`?")
        
        # Validate payload if provided
        if payload:
            validation = self.validator.validate_payload(endpoint, payload)
            if not validation.valid:
                lines.append("")
                lines.append("**Payload Issues:**")
                for error in validation.errors:
                    lines.append(f"  - {error}")
                if validation.suggestions:
                    lines.append("")
                    lines.append("**Suggestions:**")
                    for suggestion in validation.suggestions:
                        lines.append(f"  - {suggestion}")
        
        return "\n".join(lines)
    
    def _format_generic_error(self, error_msg: str, endpoint: str) -> str:
        """Format generic error message."""
        lines = ["❌ API Error"]
        lines.append("")
        lines.append(error_msg)
        lines.append("")
        lines.append(f"**Endpoint:** {endpoint}")
        
        # Try to get endpoint suggestion
        suggestion = self.validator.get_endpoint_suggestion(f"operation on {endpoint}")
        if suggestion:
            lines.append("")
            lines.append(f"💡 **Suggestion:** Consider using `{suggestion}`")
        
        return "\n".join(lines)


# Global error handler instance
_error_handler_instance: Optional[EverflowErrorHandler] = None


def get_error_handler() -> EverflowErrorHandler:
    """Get or create global error handler instance."""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = EverflowErrorHandler()
    return _error_handler_instance


