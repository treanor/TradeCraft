"""
Database utility functions for TradeCraft.
Handles CRUD operations for users, trades, trade legs, and tags.
All functions use type hints and are documented.
"""
import sqlite3
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
