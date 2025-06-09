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
    """Get a SQLite connection to the database."""
    return sqlite3.connect(db_path)


def fetch_trades_for_user(username: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all trades for a given username."""
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
    """Fetch all trade legs for a given trade ID."""
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
    """Return True if the trade is open (sum of open quantity > 0), else False."""
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
    """Insert a new trade and return its ID."""
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
    """Insert a new trade leg and return its ID."""
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trade_id, action, quantity, price, fees, executed_at, notes, now, now))
        conn.commit()
        return cur.lastrowid
