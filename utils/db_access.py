"""
Database access utilities for Trade Craft.

Provides type-annotated functions for querying and manipulating trades and trade legs.
"""

import sqlite3
import os
from pathlib import Path
from typing import Any, List, Dict, Optional
from datetime import datetime

def get_db_path() -> Path:
    """Get the database path from configuration, checking environment variables."""
    return Path(os.getenv("DB_PATH", os.getenv("DATABASE_PATH", "data/tradecraft.db")))

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get a SQLite connection to the database.
    Args:
        db_path: Path to the SQLite database file. If None, uses configured path.
    Returns:
        sqlite3.Connection object.
    """
    if db_path is None:
        db_path = get_db_path()
    return sqlite3.connect(db_path)


def fetch_trades_for_user(username: str, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Fetch all trades for a given username.
    Args:
        username: The username to fetch trades for.
        db_path: Path to the SQLite database file. If None, uses configured path.
    Returns:
        List of trade dictionaries.
    """
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT t.* FROM trades t
            JOIN users u ON t.user_id = u.id
            WHERE u.username = ?
            ORDER BY t.opened_at DESC
        ''', (username,))
        return [dict(row) for row in cur.fetchall()]


def fetch_trades_for_account(account_id: int, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Fetch all trades for a given account_id.
    Args:
        account_id: The account ID to fetch trades for.
        db_path: Path to the SQLite database file. If None, uses configured path.
    Returns:
        List of trade dictionaries.
    """
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trades
            WHERE account_id = ?
            ORDER BY opened_at DESC
        ''', (account_id,))
        return [dict(row) for row in cur.fetchall()]


def fetch_trades_for_user_and_account(user_id: int, account_id: int, db_path: Optional[Path] = None) -> list[dict]:
    """Fetch all trades for a given user_id and account_id."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trades
            WHERE user_id = ? AND account_id = ?
            ORDER BY opened_at DESC
        ''', (user_id, account_id))
        return [dict(row) for row in cur.fetchall()]


def fetch_all_trades(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Fetch all trades from the database.
    
    This follows MVVM principles - the Model layer simply provides data access,
    while filtering logic is handled at the ViewModel layer.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses configured path.
    Returns:
        List of trade dictionaries.
    """
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trades
            ORDER BY opened_at DESC
        ''')
        return [dict(row) for row in cur.fetchall()]


def fetch_legs_for_trade(trade_id: int, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Fetch all trade legs for a given trade ID.
    Args:
        trade_id: The trade ID to fetch legs for.
        db_path: Path to the SQLite database file.
    Returns:
        List of trade leg dictionaries.
    """
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trade_legs
            WHERE trade_id = ?
            ORDER BY executed_at ASC
        ''', (trade_id,))
        return [dict(row) for row in cur.fetchall()]


def is_trade_open(trade_id: int, db_path: Optional[Path] = None) -> bool:
    """
    Return True if the trade is open (sum of open quantity > 0), else False.
    Args:
        trade_id: The trade ID to check.
        db_path: Path to the SQLite database file.
    Returns:
        True if trade is open, False otherwise.
    """
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT action, SUM(quantity) as qty FROM trade_legs
            WHERE trade_id = ?
            GROUP BY action
        ''', (trade_id,))
        qty = 0
        for action, q in cur.fetchall():
            if action in ("buy", "buy to open"):
                qty += q
            elif action in ("sell", "sell to close"):
                qty -= q
        return qty > 0


def insert_trade(user_id: int, account_id: int, asset_symbol: str, asset_type: str, opened_at: str, notes: str = "", tags: str = "", db_path: Optional[Path] = None) -> int:
    """
    Insert a new trade and return its ID.
    Args:
        user_id: The user ID for the trade.
        account_id: The account ID for the trade.
        asset_symbol: The asset symbol (string or list).
        asset_type: The asset type.
        opened_at: ISO datetime string for when the trade was opened.
        notes: Optional notes for the trade.
        tags: Optional tags for the trade (comma-separated string or list).
        db_path: Path to the SQLite database file.
    Returns:
        The new trade's ID.
    """
    if db_path is None:
        db_path = get_db_path()
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trades (user_id, account_id, asset_symbol, asset_type, opened_at, notes, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, account_id, asset_symbol if isinstance(asset_symbol, str) else ",".join(asset_symbol), asset_type, opened_at, notes, tags if isinstance(tags, str) else ",".join(tags), now, now))
        trade_id = cur.lastrowid
        # --- Insert tags into tags/trade_tags tables ---
        tag_list = tags.split(",") if isinstance(tags, str) else tags
        for tag in tag_list:
            tag = tag.strip().lower()
            if not tag:
                continue
            cur.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            row = cur.fetchone()
            if row:
                tag_id = row[0]
            else:
                cur.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
                tag_id = cur.lastrowid
            cur.execute('INSERT OR IGNORE INTO trade_tags (trade_id, tag_id) VALUES (?, ?)', (trade_id, tag_id))
        # --- Insert symbols into symbols/trade_symbols tables ---
        symbol_list = asset_symbol.split(",") if isinstance(asset_symbol, str) else asset_symbol
        for symbol in symbol_list:
            symbol = symbol.strip().upper()
            if not symbol:
                continue
            cur.execute('SELECT id FROM symbols WHERE symbol = ?', (symbol,))
            row = cur.fetchone()
            if row:
                symbol_id = row[0]
            else:
                cur.execute('INSERT INTO symbols (symbol) VALUES (?)', (symbol,))
                symbol_id = cur.lastrowid
            cur.execute('INSERT OR IGNORE INTO trade_symbols (trade_id, symbol_id) VALUES (?, ?)', (trade_id, symbol_id))
        conn.commit()
        return trade_id


def insert_trade_leg(trade_id: int, action: str, quantity: int, price: float, fees: float, executed_at: str, notes: str = "", db_path: Optional[Path] = None) -> int:
    """
    Insert a new trade leg and return its ID.
    Args:
        trade_id: The trade ID this leg belongs to.
        action: The action (buy, sell, etc.).
        quantity: The quantity for this leg.
        price: The price for this leg.
        fees: The fees for this leg.
        executed_at: ISO datetime string for when the leg was executed.
        notes: Optional notes for the leg.
        db_path: Path to the SQLite database file.
    Returns:
        The new trade leg's ID.
    """
    if db_path is None:
        db_path = get_db_path()
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trade_id, action, quantity, price, fees, executed_at, notes, now, now))
        conn.commit()
        # --- Set closed_at if trade is now closed ---
        # Check if trade is now closed
        cur.execute('''
            SELECT action, SUM(quantity) as qty FROM trade_legs
            WHERE trade_id = ?
            GROUP BY action
        ''', (trade_id,))
        qty = 0
        for row in cur.fetchall():
            act, q = row
            if act in ("buy", "buy to open"):
                qty += q
            elif act in ("sell", "sell to close"):
                qty -= q
        if qty == 0:
            # Trade is closed, set closed_at if not already set
            cur.execute('SELECT closed_at FROM trades WHERE id = ?', (trade_id,))
            closed_at_val = cur.fetchone()
            if closed_at_val and closed_at_val[0] is None:
                # Find latest executed_at of any closing leg
                cur.execute('''
                    SELECT MAX(executed_at) FROM trade_legs WHERE trade_id = ? AND action IN ("sell", "sell to close")
                ''', (trade_id,))
                last_close = cur.fetchone()[0]
                if last_close:
                    cur.execute('UPDATE trades SET closed_at = ? WHERE id = ?', (last_close, trade_id))
                    conn.commit()
        return cur.lastrowid


def trade_analytics(trade_id: int, db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Calculate analytics for a trade: total P&L, average price, total fees, and open/closed status.
    Args:
        trade_id: The trade ID to analyze.
        db_path: Path to the SQLite database file.
    Returns:
        Dictionary with analytics: total_bought, total_sold, avg_buy_price, avg_sell_price, total_fees, realized_pnl, open_qty, status.
    """
    if db_path is None:
        db_path = get_db_path()
    legs = fetch_legs_for_trade(trade_id, db_path)
    total_bought = sum(l['quantity'] for l in legs if l['action'] in ("buy", "buy to open"))
    total_sold = sum(l['quantity'] for l in legs if l['action'] in ("sell", "sell to close"))
    buy_amount = sum(l['quantity'] * l['price'] for l in legs if l['action'] in ("buy", "buy to open"))
    sell_amount = sum(l['quantity'] * l['price'] for l in legs if l['action'] in ("sell", "sell to close"))
    total_fees = sum(l['fees'] for l in legs)
    avg_buy_price = (buy_amount / total_bought) if total_bought else 0.0
    avg_sell_price = (sell_amount / total_sold) if total_sold else 0.0
    realized_pnl = sell_amount - buy_amount - total_fees
    open_qty = total_bought - total_sold
    
    # Determine status based on trade outcome
    if open_qty > 0:
        status = "OPEN"
    elif realized_pnl > 0:
        status = "WIN"
    elif realized_pnl < 0:
        status = "LOSS"
    else:
        status = "BREAK-EVEN"  # For trades with exactly $0 P&L
    
    return {
        "trade_id": trade_id,
        "total_bought": total_bought,
        "total_sold": total_sold,
        "avg_buy_price": avg_buy_price,
        "avg_sell_price": avg_sell_price,
        "total_fees": total_fees,
        "realized_pnl": realized_pnl,
        "open_qty": open_qty,
        "status": status,
    }


def get_tags_for_trade(trade_id: int, db_path: Optional[Path] = None) -> list[str]:
    """Return a list of tag names for a given trade."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT tags.name FROM tags
            JOIN trade_tags ON tags.id = trade_tags.tag_id
            WHERE trade_tags.trade_id = ?
        ''', (trade_id,))
        return [row[0] for row in cur.fetchall()]


def get_all_tags(db_path: Optional[Path] = None) -> list[str]:
    """Return all unique tag names in the system."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name FROM tags ORDER BY name')
        return [row[0] for row in cur.fetchall()]


def set_tags_for_trade(trade_id: int, tags: list[str], db_path: Optional[Path] = None) -> None:
    """Set the tags for a trade, replacing any existing tags."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        # Remove existing
        cur.execute('DELETE FROM trade_tags WHERE trade_id = ?', (trade_id,))
        # Insert new tags
        for tag in tags:
            tag = tag.strip().lower()
            cur.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            row = cur.fetchone()
            if row:
                tag_id = row[0]
            else:
                cur.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
                tag_id = cur.lastrowid
            cur.execute('INSERT OR IGNORE INTO trade_tags (trade_id, tag_id) VALUES (?, ?)', (trade_id, tag_id))
        conn.commit()


def get_symbols_for_trade(trade_id: int, db_path: Optional[Path] = None) -> list[str]:
    """Return a list of symbols for a given trade."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT symbols.symbol FROM symbols
            JOIN trade_symbols ON symbols.id = trade_symbols.symbol_id
            WHERE trade_symbols.trade_id = ?
        ''', (trade_id,))
        return [row[0] for row in cur.fetchall()]


def get_all_symbols(db_path: Optional[Path] = None) -> list[str]:
    """Return all unique symbols in the system."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT symbol FROM symbols ORDER BY symbol')
        return [row[0] for row in cur.fetchall()]


def set_symbols_for_trade(trade_id: int, symbols: list[str], db_path: Optional[Path] = None) -> None:
    """Set the symbols for a trade, replacing any existing symbols."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        # Remove existing
        cur.execute('DELETE FROM trade_symbols WHERE trade_id = ?', (trade_id,))
        # Insert new symbols
        for symbol in symbols:
            symbol = symbol.strip().upper()
            cur.execute('SELECT id FROM symbols WHERE symbol = ?', (symbol,))
            row = cur.fetchone()
            if row:
                symbol_id = row[0]
            else:
                cur.execute('INSERT INTO symbols (symbol) VALUES (?)', (symbol,))
                symbol_id = cur.lastrowid
            cur.execute('INSERT OR IGNORE INTO trade_symbols (trade_id, symbol_id) VALUES (?, ?)', (trade_id, symbol_id))
        conn.commit()


def get_all_users(db_path: Optional[Path] = None) -> list[dict]:
    """Return all users as a list of dicts with id and username."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM users ORDER BY username')
        return [{"id": row[0], "username": row[1]} for row in cur.fetchall()]


def get_accounts_for_user(user_id: int, db_path: Optional[Path] = None) -> list[dict]:
    """Return all accounts for a user as a list of dicts with id, name, broker."""
    if db_path is None:
        db_path = get_db_path()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name, broker FROM accounts WHERE user_id = ? ORDER BY name', (user_id,))
        return [{"id": row[0], "name": row[1], "broker": row[2]} for row in cur.fetchall()]
