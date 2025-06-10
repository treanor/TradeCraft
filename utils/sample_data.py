"""
Sample data generation for Trade Craft (development only).

This script populates the database with sample users, accounts, trades, tags, and symbols.
Run this only in development environments.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from utils.db_init import get_connection, create_schema, DB_PATH
import random
from random import choice, randint, random, sample

def insert_sample_data(db_path: Path = DB_PATH) -> None:
    """Insert sample users, accounts, trades, tags, and symbols for development/testing."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    # Clean all tables
    cur.executescript('''
        DELETE FROM trade_symbols;
        DELETE FROM trade_tags;
        DELETE FROM trade_legs;
        DELETE FROM trades;
        DELETE FROM accounts;
        DELETE FROM users;
        DELETE FROM tags;
        DELETE FROM symbols;
    ''')
    conn.commit()
    # Users
    users = [
        ("alice", "alice@example.com", "hash1"),
        ("bob", "bob@example.com", "hash2"),
    ]
    cur.executemany("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", users)
    conn.commit()
    cur.execute("SELECT id, username FROM users")
    user_map = {row[1]: row[0] for row in cur.fetchall()}
    # Accounts (2 per user, no duplicates)
    now = datetime.now().astimezone().isoformat()
    accounts = []
    for username in user_map:
        for i in range(2):
            accounts.append((user_map[username], f"{username}_acct{i+1}", "BrokerX", f"{username}-00{i+1}", now, now))
    cur.executemany("INSERT INTO accounts (user_id, name, broker, account_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", accounts)
    conn.commit()
    cur.execute("SELECT id, user_id, name FROM accounts")
    account_map = {(row[1], row[2]): row[0] for row in cur.fetchall()}
    # Tags
    tag_names = ["swing", "daytrade", "earnings", "options", "longterm", "scalp"]
    cur.executemany("INSERT INTO tags (name) VALUES (?)", [(t,) for t in tag_names])
    conn.commit()
    cur.execute("SELECT id, name FROM tags")
    tag_map = {row[1]: row[0] for row in cur.fetchall()}
    # Symbols
    symbol_names = ["AAPL", "TSLA", "MSFT", "GOOG", "SPY", "QQQ"]
    cur.executemany("INSERT INTO symbols (symbol) VALUES (?)", [(s,) for s in symbol_names])
    conn.commit()
    cur.execute("SELECT id, symbol FROM symbols")
    symbol_map = {row[1]: row[0] for row in cur.fetchall()}
    # --- Generate trades: 1 per account per weekday for 3 months ---
    today = datetime.now().astimezone().date()
    start_date = today - timedelta(days=90)
    weekdays = []
    d = start_date
    while d <= today:
        if d.weekday() < 5:
            weekdays.append(d)
        d += timedelta(days=1)
    trade_rows = []
    trade_meta = []  # Store (is_open, is_win, entry_price, exit_price, qty, tag_ids, symbol)
    for user, user_id in user_map.items():
        for acct_num in range(1, 3):
            acct = f"{user}_acct{acct_num}"
            account_id = account_map[(user_id, acct)]
            for day in weekdays:
                symbol = choice(symbol_names)
                asset_type = "stock"
                open_dt = datetime.combine(day, datetime.min.time()).replace(hour=14, minute=30).astimezone()
                close_dt = datetime.combine(day, datetime.min.time()).replace(hour=20, minute=0).astimezone()
                is_open = random() < 0.2 or close_dt > datetime.now().astimezone()
                is_win = random() < 0.5
                entry_price = randint(90, 110)
                exit_price = entry_price + randint(1, 10) if is_win else entry_price - randint(1, 10)
                notes = f"Sample trade for {user} on {symbol}"
                created_at = open_dt.isoformat()
                updated_at = (close_dt if not is_open and close_dt <= datetime.now().astimezone() else open_dt).isoformat()
                tag_ids = sample(list(tag_map.values()), k=randint(1, 2))
                qty = randint(1, 20)
                trade_rows.append((user_id, account_id, symbol, asset_type, open_dt.isoformat(), close_dt.isoformat() if not is_open and close_dt <= datetime.now().astimezone() else None, notes, created_at, updated_at))
                trade_meta.append((is_open, is_win, entry_price, exit_price, qty, tag_ids, symbol))
    cur.executemany("""
        INSERT INTO trades (user_id, account_id, asset_symbol, asset_type, opened_at, closed_at, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trade_rows)
    conn.commit()
    # Fetch the actual trade IDs in insertion order
    cur.execute("SELECT id FROM trades ORDER BY id ASC")
    trade_ids = [row[0] for row in cur.fetchall()]
    # Now insert tags, symbols, and legs using the correct trade IDs
    trade_tags = []
    trade_symbols = []
    trade_legs = []
    for idx, trade_id in enumerate(trade_ids):
        is_open, is_win, entry_price, exit_price, qty, tag_ids, symbol = trade_meta[idx]
        for tag_id in tag_ids:
            trade_tags.append((trade_id, tag_id))
        symbol_id = symbol_map[symbol]
        trade_symbols.append((trade_id, symbol_id))
        # Legs
        open_dt = trade_rows[idx][4]
        close_dt = trade_rows[idx][5]
        created_at = trade_rows[idx][7]
        updated_at = trade_rows[idx][8]
        open_leg = (trade_id, "buy", qty, entry_price, round(random(), 2), open_dt, "Open leg", created_at, updated_at)
        trade_legs.append(open_leg)
        if not is_open and close_dt:
            close_leg = (trade_id, "sell", qty, exit_price, round(random(), 2), close_dt, "Close leg", created_at, updated_at)
            trade_legs.append(close_leg)
    cur.executemany("INSERT INTO trade_tags (trade_id, tag_id) VALUES (?, ?)", trade_tags)
    cur.executemany("INSERT INTO trade_symbols (trade_id, symbol_id) VALUES (?, ?)", trade_symbols)
    cur.executemany("""
        INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trade_legs)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_schema(get_connection())
    insert_sample_data()
    print("Sample data inserted.")
