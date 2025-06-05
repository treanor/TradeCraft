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


def rerun() -> None:
    """Compatibility wrapper for Streamlit rerun.

    Uses ``st.experimental_rerun`` when available and falls back to
    ``st.rerun`` in newer versions of Streamlit. Raises ``RuntimeError``
    if neither method exists.
    """
    import streamlit as st

    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        raise RuntimeError("Streamlit rerun not supported in this version")
