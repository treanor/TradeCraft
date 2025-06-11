"""
Tests for validation utilities.
"""

import pytest
from utils.validation import (
    validate_trade_data,
    validate_trade_leg_data,
    validate_user_data,
    sanitize_input,
    validate_date_range
)

def test_validate_trade_data():
    """Test trade data validation."""
    # Valid data
    is_valid, errors = validate_trade_data(
        symbol="AAPL",
        asset_type="stock",
        opened_at="2024-01-15T09:30:00",
        notes="Test trade",
        tags="momentum,breakout"
    )
    assert is_valid
    assert len(errors) == 0
    
    # Invalid symbol
    is_valid, errors = validate_trade_data(
        symbol="",
        asset_type="stock",
        opened_at="2024-01-15T09:30:00"
    )
    assert not is_valid
    assert "Symbol is required" in errors
    
    # Invalid asset type
    is_valid, errors = validate_trade_data(
        symbol="AAPL",
        asset_type="invalid",
        opened_at="2024-01-15T09:30:00"
    )
    assert not is_valid
    assert "Asset type must be one of" in errors[0]
    
    # Invalid datetime
    is_valid, errors = validate_trade_data(
        symbol="AAPL",
        asset_type="stock",
        opened_at="invalid-date"
    )
    assert not is_valid
    assert "Invalid datetime format" in errors[0]

def test_validate_trade_leg_data():
    """Test trade leg data validation."""
    # Valid data
    is_valid, errors = validate_trade_leg_data(
        action="buy",
        quantity=100,
        price=150.00,
        fees=1.00,
        executed_at="2024-01-15T09:30:00"
    )
    assert is_valid
    assert len(errors) == 0
    
    # Invalid quantity
    is_valid, errors = validate_trade_leg_data(
        action="buy",
        quantity=0,
        price=150.00,
        fees=1.00,
        executed_at="2024-01-15T09:30:00"
    )
    assert not is_valid
    assert "Quantity must be greater than 0" in errors
    
    # Invalid price
    is_valid, errors = validate_trade_leg_data(
        action="buy",
        quantity=100,
        price=-10.00,
        fees=1.00,
        executed_at="2024-01-15T09:30:00"
    )
    assert not is_valid
    assert "Price must be greater than 0" in errors

def test_validate_user_data():
    """Test user data validation."""
    # Valid data
    is_valid, errors = validate_user_data(
        username="testuser",
        email="test@example.com"
    )
    assert is_valid
    assert len(errors) == 0
    
    # Invalid username
    is_valid, errors = validate_user_data(username="ab")
    assert not is_valid
    assert "Username must be at least 3 characters" in errors
    
    # Invalid email
    is_valid, errors = validate_user_data(
        username="testuser",
        email="invalid-email"
    )
    assert not is_valid
    assert "Invalid email format" in errors

def test_sanitize_input():
    """Test input sanitization."""
    # Normal input
    result = sanitize_input("  normal text  ")
    assert result == "normal text"
    
    # Input with control characters
    result = sanitize_input("text\x00with\x08control\x1fchars")
    assert result == "textwithcontrolchars"
    
    # Empty input
    result = sanitize_input("")
    assert result == ""
    
    # None input
    result = sanitize_input(None)
    assert result == ""

def test_validate_date_range():
    """Test date range validation."""
    # Valid range
    is_valid, errors = validate_date_range(
        "2024-01-01",
        "2024-01-31"
    )
    assert is_valid
    assert len(errors) == 0
    
    # Invalid range (start after end)
    is_valid, errors = validate_date_range(
        "2024-01-31",
        "2024-01-01"
    )
    assert not is_valid
    assert "Start date cannot be after end date" in errors
    
    # Invalid date format
    is_valid, errors = validate_date_range(
        "invalid-date",
        "2024-01-31"
    )
    assert not is_valid
    assert "Invalid date format" in errors[0]