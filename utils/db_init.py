"""
Database initialization and sample data population for Trade Craft.

This script creates the SQLite schema and populates it with sample data for development.
"""

import sqlite3
from pathlib import Path
from typing import Any
import random
from datetime import datetime, timedelta

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


def insert_sample_data(conn: sqlite3.Connection) -> None:
    """Insert robust sample users, trades, and trade legs for development (1 trade per weekday, 3 months)."""
    cur = conn.cursor()
    # Insert users
    users = [
        ("alice", "alice@example.com", ""),
        ("bob", "bob@example.com", "")
    ]
    for username, email, password_hash in users:
        cur.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
    cur.execute("SELECT id, username FROM users")
    user_map = {row[1]: row[0] for row in cur.fetchall()}
    # Insert sample accounts for each user
    cur.execute('SELECT id FROM users')
    user_ids = [row[0] for row in cur.fetchall()]
    account_map = {}
    for user_id in user_ids:
        now = datetime.now().isoformat()
        account_ids = []
        for name, broker in [
            ("Main Account", "IBKR"),
            ("IRA Account", "Fidelity")
        ]:
            # Check if account already exists for this user and name
            cur.execute('SELECT id FROM accounts WHERE user_id = ? AND name = ?', (user_id, name))
            row = cur.fetchone()
            if row:
                account_id = row[0]
            else:
                cur.execute('INSERT INTO accounts (user_id, name, broker, created_at, updated_at) VALUES (?, ?, ?, ?, ?)', (user_id, name, broker, now, now))
                account_id = cur.lastrowid
            account_ids.append(account_id)
        account_map[user_id] = account_ids  # List of both accounts

    # --- Move assets definition here so it's in scope for trade insertion ---
    assets = [
        ("SPY", "stock"), ("AAPL", "stock"), ("TSLA", "stock"), ("QQQ", "stock"),
        ("BTCUSD", "crypto"), ("ETHUSD", "crypto"), ("ESM25", "future"), ("NQH25", "future"),
        ("EURUSD", "forex"), ("NFLX", "stock"), ("MSFT", "stock"), ("AMD", "stock"),
        ("GOOG", "stock"), ("AMZN", "stock"), ("NVDA", "stock"), ("META", "stock"),
        ("SPY 2025C400", "option"), ("AAPL 2025P150", "option"), ("TSLA 2025C800", "option")
    ]

    # --- Move per-account trade day generation and trade insertion logic here ---
    # Generate 3 months of all days (weekdays and weekends)
    start_date = datetime.now().date() - timedelta(days=90)
    all_days = []
    d = start_date
    while d <= datetime.now().date():
        all_days.append(d)
        d += timedelta(days=1)
    # Build per-account trade days: all weekdays + at least one trade per weekend (Sat/Sun)
    account_trade_days = {}
    for user_id, account_ids in account_map.items():
        for account_id in account_ids:
            # Weekdays for this account
            trade_days = [d for d in all_days if d.weekday() < 5]
            # For each weekend, ensure at least one trade (randomly Sat or Sun)
            weekends = {}
            for d in all_days:
                if d.weekday() >= 5:
                    year_week = (d.isocalendar().year, d.isocalendar().week)
                    if year_week not in weekends:
                        weekends[year_week] = []
                    weekends[year_week].append(d)
            for days in weekends.values():
                chosen = random.choice(days)
                trade_days.append(chosen)
            # Remove duplicates and sort
            trade_days = sorted(set(trade_days))
            account_trade_days[account_id] = trade_days
    # Insert trades and legs for each account
    trade_id_map = {}
    trade_idx = 0
    tag_name_to_id = {}
    symbol_to_id = {}
    def get_or_create_tag_id(tag: str) -> int:
        tag = tag.strip().lower()
        if tag in tag_name_to_id:
            return tag_name_to_id[tag]
        cur.execute('SELECT id FROM tags WHERE name = ?', (tag,))
        row = cur.fetchone()
        if row:
            tag_id = row[0]
        else:
            cur.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
            tag_id = cur.lastrowid
        tag_name_to_id[tag] = tag_id
        return tag_id
    def get_or_create_symbol_id(symbol: str) -> int:
        symbol = symbol.strip().upper()
        if symbol in symbol_to_id:
            return symbol_to_id[symbol]
        cur.execute('SELECT id FROM symbols WHERE symbol = ?', (symbol,))
        row = cur.fetchone()
        if row:
            symbol_id = row[0]
        else:
            cur.execute('INSERT INTO symbols (symbol) VALUES (?)', (symbol,))
            symbol_id = cur.lastrowid
        symbol_to_id[symbol] = symbol_id
        return symbol_id
    for user_id, account_ids in account_map.items():
        for account_id in account_ids:
            trade_days = account_trade_days[account_id]
            for trade_date in trade_days:
                asset_symbol, asset_type = random.choice(assets)
                opened_at = datetime.combine(trade_date, datetime.min.time()).replace(hour=9, minute=30)
                notes = f"Sample trade for {asset_symbol} on {trade_date}"
                tags = random.choice(["momentum,largecap", "swing,tech", "daytrade,crypto", "options,volatility", "trend,forex"])
                now_iso = datetime.now().isoformat()
                leave_open = (trade_idx % 5 == 0)  # every 5th trade is open
                closed_at = None
                cur.execute(
                    "INSERT INTO trades (user_id, account_id, asset_symbol, asset_type, opened_at, closed_at, notes, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, account_id, asset_symbol, asset_type, opened_at.isoformat(), closed_at, notes, tags, now_iso, now_iso)
                )
                trade_id = cur.lastrowid
                trade_id_map[trade_idx] = trade_id
                # --- Insert tags into tags/trade_tags tables ---
                for tag in tags.split(","):
                    tag_id = get_or_create_tag_id(tag)
                    cur.execute('INSERT OR IGNORE INTO trade_tags (trade_id, tag_id) VALUES (?, ?)', (trade_id, tag_id))
                # --- Insert symbol into symbols/trade_symbols tables ---
                symbol_id = get_or_create_symbol_id(asset_symbol)
                cur.execute('INSERT OR IGNORE INTO trade_symbols (trade_id, symbol_id) VALUES (?, ?)', (trade_id, symbol_id))
                # Generate 2-4 legs per trade
                legs = []
                qty = random.choice([10, 20, 50, 100])
                price = round(random.uniform(10, 500), 2)
                fees = round(random.uniform(0.1, 2.5), 2)
                # Buy to open
                leg_time = opened_at + timedelta(minutes=5)
                if leg_time > datetime.now().replace(hour=16, minute=0, second=0, microsecond=0):
                    leg_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
                legs.append((trade_id, "buy to open", qty, price, fees, leg_time, "Open position"))
                # Optionally add to position
                if random.random() > 0.5:
                    add_qty = random.choice([10, 20, 50])
                    add_price = round(price + random.uniform(-2, 2), 2)
                    add_fees = round(random.uniform(0.1, 2.5), 2)
                    add_time = opened_at + timedelta(minutes=60)
                    if add_time > datetime.now().replace(hour=16, minute=0, second=0, microsecond=0):
                        add_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
                    legs.append((trade_id, "buy to open", add_qty, add_price, add_fees, add_time, "Add to position"))
                    qty += add_qty
                # Partial sell (only for closed trades)
                hold_days_partial = None
                if not leave_open and random.random() > 0.3:
                    sell_qty = random.randint(1, qty-1)
                    if trade_idx % 2 == 0:
                        sell_price = round(price - random.uniform(10, 30), 2)
                    else:
                        sell_price = round(price + random.uniform(10, 30), 2)
                    sell_fees = round(random.uniform(0.1, 2.5), 2)
                    hold_days_partial = random.randint(1, 5)
                    sell_time = opened_at + timedelta(days=hold_days_partial, minutes=15)
                    if sell_time > datetime.now().replace(hour=16, minute=0, second=0, microsecond=0):
                        sell_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
                    legs.append((trade_id, "sell to close", sell_qty, sell_price, sell_fees, sell_time, "Partial exit"))
                    qty -= sell_qty
                # Final sell (only for closed trades)
                if not leave_open:
                    if trade_idx % 2 == 0:
                        sell_price = round(price - random.uniform(10, 30), 2)
                    else:
                        sell_price = round(price + random.uniform(10, 30), 2)
                    sell_fees = round(random.uniform(0.1, 2.5), 2)
                    if hold_days_partial is not None:
                        hold_days_final = hold_days_partial + random.randint(1, 5)
                    else:
                        hold_days_final = random.randint(2, 10)
                    final_time = opened_at + timedelta(days=hold_days_final, minutes=30)
                    if final_time > datetime.now().replace(hour=16, minute=0, second=0, microsecond=0):
                        final_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
                    legs.append((trade_id, "sell to close", qty, sell_price, sell_fees, final_time, "Final exit"))
                # Insert legs
                for leg in legs:
                    now_iso = datetime.now().isoformat()
                    cur.execute(
                        "INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (leg[0], leg[1], leg[2], leg[3], leg[4], leg[5].isoformat(), leg[6], now_iso, now_iso)
                    )
                # Set closed_at for closed trades
                if not leave_open:
                    cur.execute(
                        "SELECT MAX(executed_at) FROM trade_legs WHERE trade_id = ? AND action IN ('sell', 'sell to close')",
                        (trade_id,)
                    )
                    last_close = cur.fetchone()[0]
                    if last_close:
                        cur.execute(
                            "UPDATE trades SET closed_at = ? WHERE id = ?",
                            (last_close, trade_id)
                        )
                trade_idx += 1
    conn.commit()


def initialize_database(db_path: Path = DB_PATH) -> None:
    """Initialize the database: create schema and insert sample data."""
    conn = get_connection(db_path)
    create_schema(conn)
    insert_sample_data(conn)
    conn.close()


if __name__ == "__main__":
    initialize_database()
