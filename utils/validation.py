"""
Data validation utilities for Trade Craft.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re
from utils.exceptions import ValidationError

def validate_trade_data(
    symbol: str,
    asset_type: str,
    opened_at: str,
    notes: Optional[str] = None,
    tags: Optional[str] = None
) -> Tuple[bool, List[str]]:
    """
    Validate trade data before insertion.
    
    Args:
        symbol: Trading symbol
        asset_type: Type of asset
        opened_at: ISO datetime string
        notes: Optional notes
        tags: Optional tags string
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate symbol
    if not symbol or not symbol.strip():
        errors.append("Symbol is required")
    elif not re.match(r'^[A-Z0-9._-]+$', symbol.strip().upper()):
        errors.append("Symbol contains invalid characters")
    
    # Validate asset type
    valid_asset_types = {'stock', 'option', 'future', 'crypto', 'forex', 'other'}
    if asset_type not in valid_asset_types:
        errors.append(f"Asset type must be one of: {', '.join(valid_asset_types)}")
    
    # Validate datetime
    try:
        datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
    except ValueError:
        errors.append("Invalid datetime format for opened_at")
    
    # Validate notes length
    if notes and len(notes) > 1000:
        errors.append("Notes cannot exceed 1000 characters")
    
    # Validate tags
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        for tag in tag_list:
            if len(tag) > 50:
                errors.append(f"Tag '{tag}' exceeds 50 characters")
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                errors.append(f"Tag '{tag}' contains invalid characters")
    
    return len(errors) == 0, errors

def validate_trade_leg_data(
    action: str,
    quantity: int,
    price: float,
    fees: float,
    executed_at: str
) -> Tuple[bool, List[str]]:
    """
    Validate trade leg data before insertion.
    
    Args:
        action: Trade action (buy, sell, etc.)
        quantity: Number of shares/contracts
        price: Price per unit
        fees: Trading fees
        executed_at: ISO datetime string
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate action
    valid_actions = {'buy', 'sell', 'buy to open', 'sell to close', 'buy to close', 'sell to open'}
    if action not in valid_actions:
        errors.append(f"Action must be one of: {', '.join(valid_actions)}")
    
    # Validate quantity
    if quantity <= 0:
        errors.append("Quantity must be greater than 0")
    if quantity > 1000000:
        errors.append("Quantity seems unreasonably large")
    
    # Validate price
    if price <= 0:
        errors.append("Price must be greater than 0")
    if price > 1000000:
        errors.append("Price seems unreasonably large")
    
    # Validate fees
    if fees < 0:
        errors.append("Fees cannot be negative")
    if fees > price * quantity:
        errors.append("Fees cannot exceed total trade value")
    
    # Validate datetime
    try:
        datetime.fromisoformat(executed_at.replace('Z', '+00:00'))
    except ValueError:
        errors.append("Invalid datetime format for executed_at")
    
    return len(errors) == 0, errors

def validate_user_data(username: str, email: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate user data.
    
    Args:
        username: Username
        email: Optional email address
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate username
    if not username or not username.strip():
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters")
    elif len(username) > 50:
        errors.append("Username cannot exceed 50 characters")
    elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
        errors.append("Username can only contain letters, numbers, underscores, and hyphens")
    
    # Validate email if provided
    if email:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
    
    return len(errors) == 0, errors

def sanitize_input(value: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.
    
    Args:
        value: Input string to sanitize
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, List[str]]:
    """
    Validate date range inputs.
    
    Args:
        start_date: Start date string
        end_date: End date string
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        if start > end:
            errors.append("Start date cannot be after end date")
        
        # Check for reasonable date range (not more than 10 years)
        if (end - start).days > 3650:
            errors.append("Date range cannot exceed 10 years")
            
    except ValueError as e:
        errors.append(f"Invalid date format: {e}")
    
    return len(errors) == 0, errors