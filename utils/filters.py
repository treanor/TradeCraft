"""
Utility functions for applying filters to trade DataFrames.
Reusable for Trade Log and Analytics pages.
"""
from typing import Optional, List
import pandas as pd

def apply_trade_filters(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    symbols: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Filter the DataFrame by date range, tags, and symbols.
    Dates should be ISO strings (YYYY-MM-DD). Tags and symbols are lists of strings.
    """
    if start_date:
        df = df[df["opened_at"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["opened_at"] <= pd.to_datetime(end_date)]
    if tags:
        # Assume tags column is a list of strings or comma-separated string
        df = df[df["tags"].apply(lambda taglist: any(tag in taglist for tag in tags) if isinstance(taglist, list) else any(tag in taglist.split(",") for tag in tags))]
    if symbols:
        # Assume symbol column is a string (possibly comma-separated for multi-symbol trades)
        df = df[df["symbol"].apply(lambda s: any(sym in s.split(",") for sym in symbols))]
    return df
