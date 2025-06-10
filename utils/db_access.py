"""
Database access utilities for Trade Craft.

Provides type-annotated functions for querying and manipulating trades and trade legs.
"""

import sqlite3
from pathlib import Path
from typing import Any, List, Dict, Optional
from datetime import datetime

DB_PATH = Path("data/tradecraft.db")

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Get a SQLite connection to the database.
    Args:
        db_path: Path to the SQLite database file.
    Returns:
        sqlite3.Connection object.
    """
    return sqlite3.connect(db_path)


def fetch_trades_for_user(username: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch all trades for a given username.
    Args:
        username: The username to fetch trades for.
        db_path: Path to the SQLite database file.
    Returns:
        List of trade dictionaries.
    """
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


def fetch_legs_for_trade(trade_id: int, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch all trade legs for a given trade ID.
    Args:
        trade_id: The trade ID to fetch legs for.
        db_path: Path to the SQLite database file.
    Returns:
        List of trade leg dictionaries.
    """
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trade_legs
            WHERE trade_id = ?
            ORDER BY executed_at ASC
        ''', (trade_id,))
        return [dict(row) for row in cur.fetchall()]


def is_trade_open(trade_id: int, db_path: Path = DB_PATH) -> bool:
    """
    Return True if the trade is open (sum of open quantity > 0), else False.
    Args:
        trade_id: The trade ID to check.
        db_path: Path to the SQLite database file.
    Returns:
        True if trade is open, False otherwise.
    """
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


def insert_trade(user_id: int, asset_symbol: str, asset_type: str, opened_at: str, notes: str = "", tags: str = "", db_path: Path = DB_PATH) -> int:
    """
    Insert a new trade and return its ID.
    Args:
        user_id: The user ID for the trade.
        asset_symbol: The asset symbol.
        asset_type: The asset type.
        opened_at: ISO datetime string for when the trade was opened.
        notes: Optional notes for the trade.
        tags: Optional tags for the trade.
        db_path: Path to the SQLite database file.
    Returns:
        The new trade's ID.
    """
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trades (user_id, asset_symbol, asset_type, opened_at, notes, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, asset_symbol, asset_type, opened_at, notes, tags, now, now))
        conn.commit()
        return cur.lastrowid


def insert_trade_leg(trade_id: int, action: str, quantity: int, price: float, fees: float, executed_at: str, notes: str = "", db_path: Path = DB_PATH) -> int:
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


def trade_analytics(trade_id: int, db_path: Path = DB_PATH) -> Dict[str, Any]:
    """
    Calculate analytics for a trade: total P&L, average price, total fees, and open/closed status.
    Args:
        trade_id: The trade ID to analyze.
        db_path: Path to the SQLite database file.
    Returns:
        Dictionary with analytics: total_bought, total_sold, avg_buy_price, avg_sell_price, total_fees, realized_pnl, open_qty, status.
    """
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
    status = "open" if open_qty > 0 else "closed"
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
