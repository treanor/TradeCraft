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
    
    Args:
        df: DataFrame with trade data (expects 'opened_at', 'tags', and 'asset_symbol' columns)
        start_date: ISO date string (YYYY-MM-DD) for start of date range
        end_date: ISO date string (YYYY-MM-DD) for end of date range  
        tags: List of tag strings to filter by
        symbols: List of symbol strings to filter by
        
    Returns:
        Filtered DataFrame
    """
    # Ensure date columns are datetime for comparison and normalize timezone handling
    if (start_date or end_date) and "opened_at" in df.columns and not df.empty:
        # Use mixed format with UTC conversion to handle both timezone-aware and timezone-naive datetimes
        df["opened_at"] = pd.to_datetime(df["opened_at"], format='mixed', utc=True)
        if "closed_at" in df.columns:
            df["closed_at"] = pd.to_datetime(df["closed_at"], format='mixed', utc=True)
        
        # Convert from UTC to timezone-naive for consistent comparison and calculations
        df["opened_at"] = df["opened_at"].dt.tz_convert(None)
        if "closed_at" in df.columns:
            df["closed_at"] = df["closed_at"].dt.tz_convert(None)
    
    if start_date and "opened_at" in df.columns and not df.empty:
        start_ts = pd.to_datetime(start_date)
        # Ensure timezone-naive for consistent comparison
        if hasattr(start_ts, 'tz') and start_ts.tz is not None:
            start_ts = start_ts.tz_convert(None)
        df = df[df["opened_at"] >= start_ts]
    if end_date and "opened_at" in df.columns and not df.empty:
        end_ts = pd.to_datetime(end_date)
        # Ensure timezone-naive for consistent comparison
        if hasattr(end_ts, 'tz') and end_ts.tz is not None:
            end_ts = end_ts.tz_convert(None)
        df = df[df["opened_at"] <= end_ts]
    if tags:
        # Robust tag filtering: match if any tag in tags is in the taglist (list or string)
        def tag_match(taglist):
            if taglist is None:
                return False
            if isinstance(taglist, list):
                taglist_flat = [str(t).strip() for t in taglist if t]
            else:
                taglist_flat = [t.strip() for t in str(taglist).split(",") if t.strip()]
            return any(tag in taglist_flat for tag in tags)
        df = df[df["tags"].apply(tag_match)]
    if symbols:
        # Use asset_symbol column from raw database data (before it gets renamed to 'symbol')
        symbol_column = 'asset_symbol' if 'asset_symbol' in df.columns else 'symbol'
        df = df[df[symbol_column].apply(lambda s: any(sym in str(s).split(",") for sym in symbols))]
    return df


def normalize_tags_column(df: pd.DataFrame, tag_fetcher=None) -> pd.DataFrame:
    """
    Ensure the DataFrame has a 'tags' column as a comma-separated string for each row.
    Optionally, provide a tag_fetcher function (trade_id -> list of tags) for DB-backed normalization.
    """
    if 'tags' not in df.columns or tag_fetcher is not None:
        # Use tag_fetcher if provided, otherwise create empty tags column
        if tag_fetcher is not None:
            df['tags'] = [', '.join(tag_fetcher(row['id'])) for _, row in df.iterrows()]
        else:
            # Create empty tags column if it doesn't exist
            df['tags'] = ''
    else:
        # Normalize any list or NaN to comma-separated string
        def to_str(val):
            if isinstance(val, list):
                return ', '.join(str(t).strip() for t in val if t)
            if pd.isna(val):
                return ''
            return str(val)
        df['tags'] = df['tags'].apply(to_str)
    return df