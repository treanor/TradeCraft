"""
Database utility functions for TradeCraft.
Handles CRUD operations for users, trades, trade legs, and tags.
All functions use type hints and are documented.
"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path("data/tradecraft.db")

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Get a SQLite connection to the database.
    Args:
        db_path: Path to the SQLite database file.
    Returns:
        sqlite3.Connection object
    """
    return sqlite3.connect(db_path)

def fetch_all(query: str, params: Tuple = (), db_path: Path = DB_PATH) -> List[sqlite3.Row]:
    """
    Execute a SELECT query and return all results as a list of sqlite3.Row.
    Args:
        query: SQL SELECT query string.
        params: Query parameters.
        db_path: Path to the SQLite database file.
    Returns:
        List of sqlite3.Row
    """
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, params)
        return cur.fetchall()

def execute(query: str, params: Tuple = (), db_path: Path = DB_PATH) -> int:
    """
    Execute an INSERT/UPDATE/DELETE query.
    Args:
        query: SQL query string.
        params: Query parameters.
        db_path: Path to the SQLite database file.
    Returns:
        The last row id for INSERT, or number of rows affected for UPDATE/DELETE.
    """
    with get_connection(db_path) as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.lastrowid

def get_users(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch all users.
    Returns:
        List of user dicts.
    """
    rows = fetch_all("SELECT * FROM users", db_path=db_path)
    return [dict(row) for row in rows]

def add_user(username: str, email: Optional[str] = None, db_path: Path = DB_PATH) -> int:
    """
    Add a new user.
    Returns:
        The new user's id.
    """
    return execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        (username, email),
        db_path=db_path
    )

def get_trades(user_id: int, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch all trades for a user.
    Returns:
        List of trade dicts.
    """
    rows = fetch_all("SELECT * FROM trades WHERE user_id = ? ORDER BY created_at DESC", (user_id,), db_path=db_path)
    return [dict(row) for row in rows]

def add_trade(user_id: int, symbol: str, asset_type: str, status: str, created_at: str, journal_entry: Optional[str] = None, db_path: Path = DB_PATH) -> int:
    """
    Add a new trade.
    Returns:
        The new trade's id.
    """
    return execute(
        "INSERT INTO trades (user_id, symbol, asset_type, status, created_at, journal_entry) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, symbol, asset_type, status, created_at, journal_entry),
        db_path=db_path
    )

def get_trade_legs(trade_id: int, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch all trade legs for a trade.
    Returns:
        List of trade leg dicts.
    """
    rows = fetch_all("SELECT * FROM trade_legs WHERE trade_id = ? ORDER BY datetime ASC", (trade_id,), db_path=db_path)
    return [dict(row) for row in rows]

def add_trade_leg(trade_id: int, action: str, datetime: str, quantity: float, price: float, fee: float = 0.0, db_path: Path = DB_PATH) -> int:
    """
    Add a new trade leg.
    Returns:
        The new trade leg's id.
    """
    return execute(
        "INSERT INTO trade_legs (trade_id, action, datetime, quantity, price, fee) VALUES (?, ?, ?, ?, ?, ?)",
        (trade_id, action, datetime, quantity, price, fee),
        db_path=db_path
    )

def get_tags(trade_id: int, db_path: Path = DB_PATH) -> List[str]:
    """
    Fetch all tags for a trade.
    Returns:
        List of tag strings.
    """
    rows = fetch_all("SELECT tag FROM tags WHERE trade_id = ?", (trade_id,), db_path=db_path)
    return [row["tag"] for row in rows]

def add_tag(trade_id: int, tag: str, db_path: Path = DB_PATH) -> int:
    """
    Add a tag to a trade.
    Returns:
        The new tag's id.
    """
    return execute(
        "INSERT INTO tags (trade_id, tag) VALUES (?, ?)",
        (trade_id, tag),
        db_path=db_path
    )

def get_trades_dataframe(user_id: Optional[int] = None, db_path: Path = DB_PATH) -> pd.DataFrame:
    """
    Get trades data as a pandas DataFrame with calculated P&L.
    
    Args:
        user_id: Optional user ID to filter trades. If None, gets all trades.
        db_path: Path to the SQLite database file.
        
    Returns:
        DataFrame with trade data including calculated P&L
    """
    try:
        with get_connection(db_path) as conn:
            if user_id:
                query = """
                SELECT 
                    t.id as trade_id,
                    t.user_id,
                    t.symbol,
                    t.asset_type,
                    t.created_at,
                    t.status,
                    t.journal_entry,
                    GROUP_CONCAT(tg.tag) as tags
                FROM trades t
                LEFT JOIN tags tg ON t.id = tg.trade_id
                WHERE t.user_id = ?
                GROUP BY t.id
                ORDER BY t.created_at DESC
                """
                df = pd.read_sql_query(query, conn, params=(user_id,))
            else:
                query = """
                SELECT 
                    t.id as trade_id,
                    t.user_id,
                    t.symbol,
                    t.asset_type,
                    t.created_at,
                    t.status,
                    t.journal_entry,
                    GROUP_CONCAT(tg.tag) as tags
                FROM trades t
                LEFT JOIN tags tg ON t.id = tg.trade_id
                GROUP BY t.id
                ORDER BY t.created_at DESC
                """
                df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return pd.DataFrame()
            
            # Convert created_at to datetime
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Calculate P&L for each trade
            pnl_data = []
            for _, trade in df.iterrows():
                legs = get_trade_legs(trade['trade_id'], db_path)
                total_pnl = calculate_trade_pnl(legs)
                pnl_data.append(total_pnl)
            
            df['total_pnl'] = pnl_data
            
            return df
            
    except Exception as e:
        print(f"Error getting trades dataframe: {e}")
        return pd.DataFrame()


def calculate_trade_pnl(legs: List[Dict[str, Any]]) -> float:
    """
    Calculate P&L for a trade based on its legs.
    
    Args:
        legs: List of trade leg dictionaries
        
    Returns:
        Total P&L for the trade
    """
    if not legs:
        return 0.0
    
    total_cost = 0.0
    total_proceeds = 0.0
    
    for leg in legs:
        amount = leg['quantity'] * leg['price']
        fee = leg.get('fee', 0.0)
        
        if leg['action'] in ['buy', 'buy_to_open']:
            total_cost += amount + fee
        elif leg['action'] in ['sell', 'sell_to_close']:
            total_proceeds += amount - fee
    
    return total_proceeds - total_cost


def update_trade(trade_id: int, **kwargs) -> bool:
    """
    Update a trade with new values.
    
    Args:
        trade_id: ID of the trade to update
        **kwargs: Fields to update (symbol, status, journal_entry, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    if not kwargs:
        return False
    
    # Build the update query
    fields = []
    values = []
    for key, value in kwargs.items():
        if key in ['symbol', 'asset_type', 'status', 'journal_entry', 'created_at']:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if not fields:
        return False
    
    values.append(trade_id)
    query = f"UPDATE trades SET {', '.join(fields)} WHERE id = ?"
    
    try:
        execute(query, tuple(values))
        return True
    except Exception as e:
        print(f"Error updating trade {trade_id}: {e}")
        return False


def delete_trade(trade_id: int, db_path: Path = DB_PATH) -> bool:
    """
    Delete a trade and all its associated legs and tags.
    
    Args:
        trade_id: ID of the trade to delete
        db_path: Path to the SQLite database file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_connection(db_path) as conn:
            # Delete tags first
            conn.execute("DELETE FROM tags WHERE trade_id = ?", (trade_id,))
            # Delete legs
            conn.execute("DELETE FROM trade_legs WHERE trade_id = ?", (trade_id,))
            # Delete trade
            conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting trade {trade_id}: {e}")
        return False


def get_trade_summary_stats(user_id: Optional[int] = None, db_path: Path = DB_PATH) -> Dict[str, Any]:
    """
    Get summary statistics for trades.
    
    Args:
        user_id: Optional user ID to filter trades
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary with summary statistics
    """
    df = get_trades_dataframe(user_id, db_path)
    
    if df.empty:
        return {
            'total_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'avg_trade': 0.0
        }
    
    total_trades = len(df)
    total_pnl = df['total_pnl'].sum()
    wins = len(df[df['status'] == 'WIN'])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
    avg_trade = total_pnl / total_trades if total_trades > 0 else 0.0
    
    return {
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_trade': avg_trade
    }
