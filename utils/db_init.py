"""
Database initialization for Trade Craft.

This script creates the SQLite schema. Sample data generation is now in utils/sample_data.py.
"""

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("data/tradecraft.db")


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Get a SQLite connection to the database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create tables for users, trades, trade_legs, tags, trade_tags, symbols, and trade_symbols if they do not exist."""
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT
        )
    ''')
    # --- New: accounts table ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            broker TEXT,
            account_number TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            asset_symbol TEXT NOT NULL,
            asset_type TEXT NOT NULL CHECK(asset_type IN ('stock', 'option', 'future', 'crypto', 'forex', 'other')),
            opened_at TEXT NOT NULL,
            closed_at TEXT,
            notes TEXT,
            tags TEXT,  -- legacy, for migration only
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS trade_legs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            action TEXT NOT NULL CHECK(action IN ('buy', 'sell', 'buy to open', 'sell to close', 'buy to close', 'sell to open')),
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            fees REAL NOT NULL DEFAULT 0.0,
            executed_at TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(trade_id) REFERENCES trades(id) ON DELETE CASCADE
        )
    ''')
    # --- New: tags and trade_tags tables ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS trade_tags (
            trade_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (trade_id, tag_id),
            FOREIGN KEY(trade_id) REFERENCES trades(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')
    # --- New: symbols and trade_symbols tables ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS trade_symbols (
            trade_id INTEGER NOT NULL,
            symbol_id INTEGER NOT NULL,
            PRIMARY KEY (trade_id, symbol_id),
            FOREIGN KEY(trade_id) REFERENCES trades(id) ON DELETE CASCADE,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id) ON DELETE CASCADE
        )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_trades_asset_symbol ON trades(asset_symbol)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_trade_legs_trade_id ON trade_legs(trade_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_trade_tags_trade_id ON trade_tags(trade_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_symbols_symbol ON symbols(symbol)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_trade_symbols_trade_id ON trade_symbols(trade_id)')
    conn.commit()


def initialize_database(db_path: Path = DB_PATH) -> None:
    """Initialize the database: create schema only. Sample data is now in utils/sample_data.py."""
    conn = get_connection(db_path)
    create_schema(conn)
    conn.close()


if __name__ == "__main__":
    initialize_database()
