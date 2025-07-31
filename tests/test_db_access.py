"""
Unit tests for database access functions.
"""
import pytest
import pandas as pd
from utils import db_access


@pytest.mark.database
class TestDatabaseAccess:
    """Test database access functions."""
    
    def test_fetch_trades_for_user(self, test_db):
        """Test fetching trades for a user."""
        trades = db_access.fetch_trades_for_user("alice", test_db)
        
        assert isinstance(trades, list)
        assert len(trades) > 0
        
        # Check structure
        trade = trades[0]
        required_fields = ['id', 'asset_symbol', 'asset_type', 'opened_at']
        for field in required_fields:
            assert field in trade
    
    def test_fetch_trades_for_user_and_account(self, test_db):
        """Test fetching trades for user and account."""
        trades = db_access.fetch_trades_for_user_and_account(1, 1, test_db)
        
        assert isinstance(trades, list)
        assert len(trades) > 0
        assert all(t['user_id'] == 1 and t['account_id'] == 1 for t in trades)
    
    def test_fetch_legs_for_trade(self, test_db):
        """Test fetching legs for a trade."""
        trades = db_access.fetch_trades_for_user("alice", test_db)
        trade_id = trades[0]['id']
        
        legs = db_access.fetch_legs_for_trade(trade_id, test_db)
        
        assert isinstance(legs, list)
        assert len(legs) > 0
        
        # Check structure
        leg = legs[0]
        required_fields = ['id', 'action', 'quantity', 'price', 'fees']
        for field in required_fields:
            assert field in leg
    
    def test_trade_analytics(self, test_db):
        """Test trade analytics calculation."""
        trades = db_access.fetch_trades_for_user("alice", test_db)
        trade_id = trades[0]['id']
        
        analytics = db_access.trade_analytics(trade_id, test_db)
        
        # Check structure
        required_fields = [
            'trade_id', 'total_bought', 'total_sold', 'avg_buy_price',
            'avg_sell_price', 'total_fees', 'realized_pnl', 'open_qty', 'status'
        ]
        for field in required_fields:
            assert field in analytics
        
        # Check status values
        assert analytics['status'] in ('WIN', 'LOSS', 'OPEN', 'BREAK-EVEN')
          # Check calculations
        assert isinstance(analytics['realized_pnl'], (int, float))
        assert analytics['total_bought'] >= 0
        assert analytics['total_sold'] >= 0
    
    def test_insert_trade(self, test_db, sample_trade_data):
        """Test inserting a new trade."""
        trade_id = db_access.insert_trade(
            user_id=sample_trade_data['user_id'],
            account_id=sample_trade_data['account_id'],
            asset_symbol=sample_trade_data['asset_symbol'],
            asset_type=sample_trade_data['asset_type'],
            opened_at=sample_trade_data['opened_at'],
            notes=sample_trade_data['notes'],
            tags=sample_trade_data['tags'],
            db_path=test_db
        )
        
        assert isinstance(trade_id, int)
        assert trade_id > 0
        
        # Verify trade was inserted
        trades = db_access.fetch_trades_for_user_and_account(1, 1, test_db)
        new_trade = next((t for t in trades if t['id'] == trade_id), None)
        assert new_trade is not None
        assert new_trade['asset_symbol'] == sample_trade_data['asset_symbol']
    
    def test_insert_trade_leg(self, test_db, sample_trade_data, sample_leg_data):
        """Test inserting a trade leg."""        # First create a trade
        trade_id = db_access.insert_trade(
            user_id=sample_trade_data['user_id'],
            account_id=sample_trade_data['account_id'],
            asset_symbol=sample_trade_data['asset_symbol'],
            asset_type=sample_trade_data['asset_type'],
            opened_at=sample_trade_data['opened_at'],
            db_path=test_db
        )
        
        # Insert a leg
        leg_id = db_access.insert_trade_leg(
            trade_id=trade_id,
            action=sample_leg_data['action'],
            quantity=sample_leg_data['quantity'],
            price=sample_leg_data['price'],
            fees=sample_leg_data['fees'],
            executed_at=sample_leg_data['executed_at'],
            notes=sample_leg_data['notes'],
            db_path=test_db
        )
        
        assert isinstance(leg_id, int)
        assert leg_id > 0
        
        # Verify leg was inserted
        legs = db_access.fetch_legs_for_trade(trade_id, test_db)
        new_leg = next((l for l in legs if l['id'] == leg_id), None)
        assert new_leg is not None
        assert new_leg['action'] == sample_leg_data['action']
        assert new_leg['quantity'] == sample_leg_data['quantity']
