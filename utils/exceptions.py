"""
Custom exceptions for Trade Craft application.
"""

class TradeCraftError(Exception):
    """Base exception for Trade Craft application."""
    pass

class DatabaseError(TradeCraftError):
    """Database operation errors."""
    pass

class ValidationError(TradeCraftError):
    """Data validation errors."""
    pass

class TradeNotFoundError(TradeCraftError):
    """Trade not found errors."""
    pass

class UserNotFoundError(TradeCraftError):
    """User not found errors."""
    pass

class AccountNotFoundError(TradeCraftError):
    """Account not found errors."""
    pass

class InsufficientDataError(TradeCraftError):
    """Insufficient data for calculations."""
    pass