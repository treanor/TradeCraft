"""
Basic tests for db_access.py utility functions.
"""
import pytest
from utils import db_access

def test_fetch_trades_for_user():
    trades = db_access.fetch_trades_for_user("alice")
    assert isinstance(trades, list)
    assert len(trades) > 0
    assert all('asset_symbol' in t for t in trades)

def test_fetch_legs_for_trade():
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]['id']
    legs = db_access.fetch_legs_for_trade(trade_id)
    assert isinstance(legs, list)
    assert len(legs) > 0
    assert all('action' in l for l in legs)

def test_is_trade_open():
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]['id']
    # All sample trades should be closed by design
    assert db_access.is_trade_open(trade_id) is False

def test_insert_trade_and_leg():
    user_id = 1  # alice
    trade_id = db_access.insert_trade(user_id, "TEST", "stock", "2025-06-09T09:30:00", "test trade", "test")
    assert isinstance(trade_id, int)
    leg_id = db_access.insert_trade_leg(trade_id, "buy to open", 10, 100.0, 1.0, "2025-06-09T09:35:00", "test leg")
    assert isinstance(leg_id, int)
    # Clean up
    from utils.db_access import get_connection
    with get_connection() as conn:
        conn.execute("DELETE FROM trade_legs WHERE trade_id = ?", (trade_id,))
        conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        conn.commit()

if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))
