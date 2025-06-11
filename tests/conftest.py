"""
Pytest configuration and fixtures for Trade Craft tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sqlite3
from utils.db_init import create_schema
from utils.sample_data import insert_sample_data

@pytest.fixture(scope="session")
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_tradecraft.db"
    
    # Create schema and insert sample data
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    conn.close()
    
    insert_sample_data(db_path)
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing."""
    return {
        "user_id": 1,
        "asset_symbol": "AAPL",
        "asset_type": "stock",
        "opened_at": "2024-01-15T09:30:00",
        "notes": "Test trade",
        "tags": "test,sample"
    }

@pytest.fixture
def sample_leg_data():
    """Sample trade leg data for testing."""
    return {
        "action": "buy",
        "quantity": 100,
        "price": 150.00,
        "fees": 1.00,
        "executed_at": "2024-01-15T09:30:00",
        "notes": "Test leg"
    }