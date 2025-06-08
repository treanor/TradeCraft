from utils.db_utils import get_trade_summary_stats

stats = get_trade_summary_stats()
print("Database Status:")
print(f"  Total Trades: {stats.get('total_trades', 0)}")
print(f"  Total P&L: ${stats.get('total_pnl', 0):,.2f}")
print(f"  Win Rate: {stats.get('win_rate', 0):.1f}%")
