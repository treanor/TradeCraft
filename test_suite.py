"""
TradeCraft Application Test Suite

Comprehensive test script to validate all application functionality
including database operations, analytics, and component rendering.
"""
from typing import Dict, Any
import sys
import traceback

def test_database_operations() -> bool:
    """Test database connectivity and basic operations."""
    try:
        from utils.db_utils import get_trade_summary_stats, get_users
        
        # Test getting statistics
        stats = get_trade_summary_stats()
        assert isinstance(stats, dict), "Stats should return a dictionary"
        assert 'total_trades' in stats, "Stats should include total_trades"
        
        # Test user operations
        users = get_users()
        assert isinstance(users, list), "Users should return a list"
        
        print("✅ Database operations test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Database operations test: FAILED - {e}")
        return False


def test_analytics_functions() -> bool:
    """Test analytics calculation functions."""
    try:
        from utils.analytics import calculate_win_rate, calculate_total_pnl
        from utils.db_utils import get_trades_dataframe
        
        # Get sample data
        df = get_trades_dataframe()
        
        if len(df) > 0:
            # Test analytics functions
            win_rate = calculate_win_rate(df)
            total_pnl = calculate_total_pnl(df)
            
            assert isinstance(win_rate, (int, float)), "Win rate should be numeric"
            assert 0 <= win_rate <= 100, "Win rate should be between 0 and 100"
            assert isinstance(total_pnl, (int, float)), "Total P&L should be numeric"
            
            print("✅ Analytics functions test: PASSED")
            print(f"   Sample win rate: {win_rate:.1f}%")
            print(f"   Sample total P&L: ${total_pnl:,.2f}")
        else:
            print("⚠️ Analytics functions test: SKIPPED (no data)")
            
        return True
        
    except Exception as e:
        print(f"❌ Analytics functions test: FAILED - {e}")
        return False


def test_component_imports() -> bool:
    """Test that all components can be imported successfully."""
    try:
        # Test core imports
        import dash
        import dash_bootstrap_components as dbc
        import plotly.graph_objects as go
        import pandas as pd
        
        # Create temporary app for page registration
        temp_app = dash.Dash(__name__)
        
        # Test custom components
        from components import create_metric_card, create_page_header
        
        # Test page imports (requires app instance)
        import pages.dashboard
        import pages.trades
        import pages.analytics
        import pages.settings
        
        print("✅ Component imports test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Component imports test: FAILED - {e}")
        return False


def test_sample_data() -> bool:
    """Test sample data generation and loading."""
    try:
        from sample_data import sample_trades
        from models import Trade, AssetType, TradeAction
        
        assert len(sample_trades) > 0, "Should have sample trades"
        
        # Test first trade structure
        first_trade = sample_trades[0]
        assert isinstance(first_trade, Trade), "Should be Trade object"
        assert hasattr(first_trade, 'symbol'), "Trade should have symbol"
        assert hasattr(first_trade, 'legs'), "Trade should have legs"
        assert len(first_trade.legs) > 0, "Trade should have at least one leg"
        
        print("✅ Sample data test: PASSED")
        print(f"   Sample trades loaded: {len(sample_trades)}")
        return True
        
    except Exception as e:
        print(f"❌ Sample data test: FAILED - {e}")
        return False


def run_comprehensive_test() -> Dict[str, bool]:
    """Run all test functions and return results."""
    print("🚀 TradeCraft Application Test Suite")
    print("=" * 50)
    
    test_results = {}
    
    # Run all tests
    test_results['database'] = test_database_operations()
    test_results['analytics'] = test_analytics_functions()
    test_results['components'] = test_component_imports()
    test_results['sample_data'] = test_sample_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.title().replace('_', ' ')}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return test_results


if __name__ == "__main__":
    try:
        results = run_comprehensive_test()
        sys.exit(0 if all(results.values()) else 1)
    except Exception as e:
        print(f"💥 Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)
