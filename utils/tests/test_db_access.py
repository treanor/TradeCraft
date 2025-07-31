"""
Pytest tests for db_access.py utility functions (in utils/tests/).
"""
import pytest
from utils import db_access

def test_fetch_trades_for_user():
    """Test fetching all trades for a user returns a non-empty list with expected keys."""
    trades = db_access.fetch_trades_for_user("alice")
    assert isinstance(trades, list)
    assert len(trades) > 0
    assert all('asset_symbol' in t for t in trades)

def test_fetch_legs_for_trade():
    """Test fetching all legs for a trade returns a non-empty list with expected keys."""
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]['id']
    legs = db_access.fetch_legs_for_trade(trade_id)
    assert isinstance(legs, list)
    assert len(legs) > 0
    assert all('action' in l for l in legs)

def test_is_trade_open():
    """Test that all sample trades are closed by design."""
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]['id']
    assert db_access.is_trade_open(trade_id) is False

def test_insert_trade_and_leg():
    """Test inserting a trade and leg, then clean up."""
    user_id = 1  # alice
    account_id = 1  # alice's account
    trade_id = db_access.insert_trade(user_id, account_id, "TEST", "stock", "2025-06-09T09:30:00", "test trade", "test")
    assert isinstance(trade_id, int)
    leg_id = db_access.insert_trade_leg(trade_id, "buy to open", 10, 100.0, 1.0, "2025-06-09T09:35:00", "test leg")
    assert isinstance(leg_id, int)
    # Clean up
    from utils.db_access import get_connection
    with get_connection() as conn:
        conn.execute("DELETE FROM trade_legs WHERE trade_id = ?", (trade_id,))
        conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        conn.commit()

def test_trade_analytics():
    """Test analytics helper returns expected keys and values."""
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]["id"]
    analytics = db_access.trade_analytics(trade_id)
    assert isinstance(analytics, dict)
    assert "realized_pnl" in analytics
    assert "status" in analytics
    assert analytics["status"] in ("OPEN", "WIN", "LOSS", "BREAK-EVEN")
    assert "total_fees" in analytics
    assert analytics["total_fees"] >= 0

if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))
