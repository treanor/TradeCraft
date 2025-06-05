import pandas as pd


def aggregate_pnl(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """Aggregate P&L by a pandas offset alias (e.g., 'D', 'W', 'M')."""
    if df.empty:
        return pd.DataFrame(columns=['date', 'pnl'])
    agg = (
        df.set_index('date')['pnl']
        .resample(freq)
        .sum()
        .reset_index()
    )
    return agg
