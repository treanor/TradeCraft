#!/usr/bin/env python3
"""
Test symbol filtering functionality
"""
from utils import db_access
from utils.filters import apply_trade_filters, normalize_tags_column
import pandas as pd

def test_symbol_filtering():
    # Test symbol filtering
    user_id = 1
    account_id = 1

    trades = db_access.fetch_trades_for_user_and_account(user_id, account_id)
    df = pd.DataFrame(trades)
    print(f'Total trades: {len(df)}')
    print(f'Available columns: {list(df.columns)}')

    if not df.empty:
        # Get unique symbols
        unique_symbols = df['asset_symbol'].unique()[:5]  # Test first 5 symbols
        print(f'Sample symbols in data: {list(unique_symbols)}')
        
        # Test filtering by specific symbols
        for symbol in unique_symbols[:2]:  # Test first 2
            try:
                filtered_df = apply_trade_filters(df, None, None, None, [symbol])
                print(f'Trades with {symbol}: {len(filtered_df)}')
                if len(filtered_df) > 0:
                    sample_symbols = filtered_df['asset_symbol'].head(3).tolist()
                    print(f'  Sample filtered symbols: {sample_symbols}')
            except Exception as e:
                print(f'Error filtering {symbol}: {e}')

if __name__ == '__main__':
    test_symbol_filtering()
