"""Custom exceptions for the Riot API client."""

class RiotAPIError(Exception):
    """Base exception for Riot API related errors."""

class RiotAPIRateLimitError(RiotAPIError):
    """Exception raised when rate limit is exceeded."""

class RiotAPIUnauthorizedError(RiotAPIError):
    """Exception raised for unauthorized access (invalid API key)."""

class RiotAPINotFoundError(RiotAPIError):
    """Exception raised when the requested resource is not found."""
