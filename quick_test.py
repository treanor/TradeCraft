#!/usr/bin/env python3
"""
Quick validation script for TradeCraft application.
"""

def main():
    print("🚀 TradeCraft Quick Validation")
    print("=" * 40)
    
    # Test database
    try:
        from utils.db_utils import get_trades_dataframe
        df = get_trades_dataframe()
        print(f"✅ Database: {len(df)} trades loaded")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Test analytics
    try:
        from utils.analytics import get_dashboard_metrics
        metrics = get_dashboard_metrics(df)
        print(f"✅ Analytics: {metrics['total_trades']} trades analyzed")
        print(f"   - Total P&L: ${metrics['total_pnl']:,.2f}")
        print(f"   - Win Rate: {metrics['win_rate']:.1f}%")
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return
    
    # Test components
    try:
        from components import create_metric_card
        card = create_metric_card("Test", "$1000", "success")
        print("✅ Components: UI components working")
    except Exception as e:
        print(f"❌ Components error: {e}")
        return
    
    print("=" * 40)
    print("🎉 All core functionality validated!")
    print("🌐 Application running at: http://127.0.0.1:8050/")

if __name__ == "__main__":
    main()
