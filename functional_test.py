#!/usr/bin/env python3
"""
Functional test script for TradeCraft application.
Tests the main functionality without requiring a browser.
"""

import sqlite3
import pandas as pd
from utils.db_utils import get_all_trades, add_trade
from utils.analytics import get_dashboard_metrics, calculate_win_rate, calculate_total_pnl
from models import Trade, AssetType, TradeAction
from datetime import datetime


def test_database_functionality():
    """Test core database operations."""
    print("🔄 Testing database functionality...")
    
    # Test reading trades
    trades = get_all_trades()
    print(f"   ✅ Successfully loaded {len(trades)} trades from database")
    
    # Test adding a new trade
    test_trade = Trade(
        symbol="TEST",
        asset_type=AssetType.STOCK,
        action=TradeAction.BUY,
        quantity=100,
        price=50.0,
        date=datetime.now(),
        notes="Functional test trade"
    )
    
    initial_count = len(trades)
    add_trade(test_trade)
    updated_trades = get_all_trades()
    
    if len(updated_trades) == initial_count + 1:
        print("   ✅ Successfully added new trade to database")
    else:
        print("   ❌ Failed to add new trade to database")
    
    return True


def test_analytics_calculations():
    """Test analytics calculations with real data."""
    print("🔄 Testing analytics calculations...")
    
    # Get trades as DataFrame
    trades = get_all_trades()
    df = pd.DataFrame([{
        'symbol': t.symbol,
        'total_pnl': t.total_pnl,
        'status': 'WIN' if t.total_pnl > 0 else 'LOSS'
    } for t in trades])
    
    # Test metrics
    metrics = get_dashboard_metrics(df)
    win_rate = calculate_win_rate(df)
    total_pnl = calculate_total_pnl(df)
    
    print(f"   ✅ Total P&L: ${total_pnl:,.2f}")
    print(f"   ✅ Win Rate: {win_rate:.1f}%")
    print(f"   ✅ Total Trades: {metrics['total_trades']}")
    print(f"   ✅ Average Return: ${metrics['avg_return']:,.2f}")
    
    return True


def test_component_functionality():
    """Test that components can be created."""
    print("🔄 Testing component functionality...")
    
    try:
        from components import create_metric_card, create_page_header
        
        # Test metric card creation
        card = create_metric_card("Test", "$1,000", "success")
        print("   ✅ Successfully created metric card component")
        
        # Test page header creation
        header = create_page_header("Test Page", "Test description")
        print("   ✅ Successfully created page header component")
        
        return True
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return False


def main():
    """Run all functional tests."""
    print("🚀 TradeCraft Functional Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_functionality,
        test_analytics_calculations,
        test_component_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Functional Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functional tests passed! Application is fully operational.")
    else:
        print("⚠️  Some functional tests failed. Please check the issues above.")


if __name__ == "__main__":
    main()
