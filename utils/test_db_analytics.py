"""
Tests for analytics helper in db_access.py
"""
import pytest
from utils import db_access

def test_trade_analytics():
    trades = db_access.fetch_trades_for_user("alice")
    trade_id = trades[0]["id"]
    analytics = db_access.trade_analytics(trade_id)
    assert isinstance(analytics, dict)
    assert "realized_pnl" in analytics
    assert "status" in analytics
    assert analytics["status"] in ("OPEN", "WIN", "LOSS", "BREAK-EVEN")
    assert "total_fees" in analytics
    assert analytics["total_fees"] >= 0

def test_dummy():
    assert True

if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))
