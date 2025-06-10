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
        # Assume tags column is comma-separated string
        df = df[df["tags"].fillna("").apply(lambda t: any(tag in [x.strip() for x in t.split(",")] for tag in tags))]
    if symbols:
        df = df[df["asset_symbol"].isin(symbols)]
    return df
