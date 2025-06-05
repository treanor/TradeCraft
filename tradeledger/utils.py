import pandas as pd


def aggregate_pnl(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """Aggregate P&L by a pandas offset alias (e.g., 'D', 'W', 'M').
    'M' is mapped to 'MS' for compatibility with pandas >=2.0.
    """
    if df.empty:
        return pd.DataFrame(columns=['date', 'pnl'])
    # Map deprecated 'M' to 'MS' (month start)
    if freq == 'M':
        freq = 'MS'
    agg = (
        df.set_index('date')['pnl']
        .resample(freq)
        .sum()
        .reset_index()
    )
    return agg
