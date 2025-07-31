"""
Test configuration and fixtures.
"""
import pytest
import tempfile
import sqlite3
from pathlib import Path
from utils.db_init import create_schema, get_connection
from utils.sample_data import insert_sample_data


@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database with sample data."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = Path(tmp.name)
    
    # Initialize schema and data
    conn = get_connection(test_db_path)
    create_schema(conn)
    insert_sample_data(test_db_path)
    conn.close()
    
    # Set environment variable for tests to use this database
    import os
    old_db_path = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = str(test_db_path)
    
    yield test_db_path
    
    # Restore original environment variable
    if old_db_path is not None:
        os.environ['DATABASE_PATH'] = old_db_path
    elif 'DATABASE_PATH' in os.environ:
        del os.environ['DATABASE_PATH']
    
    # Cleanup - close any remaining connections first
    try:
        import gc
        gc.collect()  # Force garbage collection to close connections
        test_db_path.unlink(missing_ok=True)
    except PermissionError:
        # On Windows, database file might still be locked
        import time
        time.sleep(0.1)
        try:
            test_db_path.unlink(missing_ok=True)
        except PermissionError:
            pass  # If still locked, leave it for OS cleanup


@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing."""
    return {
        'user_id': 1,
        'account_id': 1,
        'asset_symbol': 'AAPL',
        'asset_type': 'stock',
        'opened_at': '2024-01-15 09:30:00',
        'notes': 'Test trade',
        'tags': 'test,sample'
    }


@pytest.fixture
def sample_leg_data():
    """Sample trade leg data for testing."""
    return {
        'action': 'buy',
        'quantity': 100,
        'price': 150.50,
        'fees': 1.00,
        'executed_at': '2024-01-15 09:30:00',
        'notes': 'Test leg'
    }
