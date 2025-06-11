"""
Comprehensive tests for database access functions.
"""

import pytest
from utils import db_access
from utils.exceptions import DatabaseError

def test_fetch_trades_for_user(temp_db):
    """Test fetching trades for a user."""
    trades = db_access.fetch_trades_for_user("alice", temp_db)
    assert isinstance(trades, list)
    assert len(trades) > 0
    assert all('asset_symbol' in t for t in trades)

def test_fetch_trades_for_user_and_account(temp_db):
    """Test fetching trades for user and account."""
    trades = db_access.fetch_trades_for_user_and_account(1, 1, temp_db)
    assert isinstance(trades, list)
    
    # Test with None values
    empty_trades = db_access.fetch_trades_for_user_and_account(None, None, temp_db)
    assert empty_trades == []

def test_insert_and_fetch_trade(temp_db, sample_trade_data):
    """Test inserting and fetching a trade."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    assert isinstance(trade_id, int)
    
    # Fetch the trade
    trades = db_access.fetch_trades_for_user_and_account(1, 1, temp_db)
    inserted_trade = next((t for t in trades if t['id'] == trade_id), None)
    assert inserted_trade is not None
    assert inserted_trade['asset_symbol'] == sample_trade_data['asset_symbol']

def test_insert_and_fetch_trade_leg(temp_db, sample_trade_data, sample_leg_data):
    """Test inserting and fetching trade legs."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    leg_id = db_access.insert_trade_leg(trade_id, **sample_leg_data, db_path=temp_db)
    
    assert isinstance(leg_id, int)
    
    legs = db_access.fetch_legs_for_trade(trade_id, temp_db)
    assert len(legs) == 1
    assert legs[0]['action'] == sample_leg_data['action']
    assert legs[0]['quantity'] == sample_leg_data['quantity']

def test_trade_analytics(temp_db):
    """Test trade analytics calculation."""
    trades = db_access.fetch_trades_for_user("alice", temp_db)
    if trades:
        trade_id = trades[0]['id']
        analytics = db_access.trade_analytics(trade_id, temp_db)
        
        assert hasattr(analytics, 'trade_id')
        assert hasattr(analytics, 'realized_pnl')
        assert hasattr(analytics, 'status')
        assert analytics.status in ('open', 'closed', 'empty')

def test_tags_operations(temp_db, sample_trade_data):
    """Test tag-related operations."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    
    # Test getting tags
    tags = db_access.get_tags_for_trade(trade_id, temp_db)
    assert isinstance(tags, list)
    
    # Test setting tags
    new_tags = ['momentum', 'breakout']
    db_access.set_tags_for_trade(trade_id, new_tags, temp_db)
    
    updated_tags = db_access.get_tags_for_trade(trade_id, temp_db)
    assert set(updated_tags) == set(new_tags)

def test_symbols_operations(temp_db, sample_trade_data):
    """Test symbol-related operations."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    
    # Test getting symbols
    symbols = db_access.get_symbols_for_trade(trade_id, temp_db)
    assert isinstance(symbols, list)
    assert sample_trade_data['asset_symbol'] in symbols

def test_performance_metrics(temp_db):
    """Test performance metrics calculation."""
    metrics = db_access.get_performance_metrics(1, 1, temp_db)
    
    assert hasattr(metrics, 'total_trades')
    assert hasattr(metrics, 'win_rate')
    assert hasattr(metrics, 'profit_factor')
    assert metrics.total_trades >= 0
    assert 0 <= metrics.win_rate <= 100

def test_delete_trade(temp_db, sample_trade_data):
    """Test trade deletion."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    
    # Verify trade exists
    trades_before = db_access.fetch_trades_for_user_and_account(1, 1, temp_db)
    trade_exists = any(t['id'] == trade_id for t in trades_before)
    assert trade_exists
    
    # Delete trade
    success = db_access.delete_trade(trade_id, temp_db)
    assert success
    
    # Verify trade is deleted
    trades_after = db_access.fetch_trades_for_user_and_account(1, 1, temp_db)
    trade_exists = any(t['id'] == trade_id for t in trades_after)
    assert not trade_exists

def test_update_trade(temp_db, sample_trade_data):
    """Test trade updates."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    
    # Update notes
    new_notes = "Updated test notes"
    success = db_access.update_trade(trade_id, notes=new_notes, db_path=temp_db)
    assert success
    
    # Verify update
    trades = db_access.fetch_trades_for_user_and_account(1, 1, temp_db)
    updated_trade = next((t for t in trades if t['id'] == trade_id), None)
    assert updated_trade['notes'] == new_notes

def test_is_trade_open(temp_db, sample_trade_data, sample_leg_data):
    """Test trade open/closed status detection."""
    trade_id = db_access.insert_trade(**sample_trade_data, db_path=temp_db)
    
    # Add buy leg
    db_access.insert_trade_leg(trade_id, **sample_leg_data, db_path=temp_db)
    assert db_access.is_trade_open(trade_id, temp_db)
    
    # Add sell leg to close
    sell_leg = sample_leg_data.copy()
    sell_leg['action'] = 'sell'
    db_access.insert_trade_leg(trade_id, **sell_leg, db_path=temp_db)
    assert not db_access.is_trade_open(trade_id, temp_db)

def test_get_all_users_and_accounts(temp_db):
    """Test fetching all users and accounts."""
    users = db_access.get_all_users(temp_db)
    assert isinstance(users, list)
    assert len(users) > 0
    assert all('id' in u and 'username' in u for u in users)
    
    # Test accounts for first user
    user_id = users[0]['id']
    accounts = db_access.get_accounts_for_user(user_id, temp_db)
    assert isinstance(accounts, list)
    assert all('id' in a and 'name' in a for a in accounts)

def test_error_handling(temp_db):
    """Test error handling in database operations."""
    # Test with invalid trade ID
    analytics = db_access.trade_analytics(99999, temp_db)
    assert analytics.status == "empty"
    
    # Test with None user_id
    trades = db_access.fetch_trades_for_user_and_account(None, 1, temp_db)
    assert trades == []