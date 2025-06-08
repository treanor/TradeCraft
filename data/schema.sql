-- SQLite schema for TradeCraft trading journal app
-- Supports users, trades, trade legs, and tags

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- e.g., 'stock', 'option'
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL,     -- e.g., 'OPEN', 'WIN', 'LOSS'
    journal_entry TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE trade_legs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    action TEXT NOT NULL,     -- e.g., 'buy', 'sell_to_open', etc.
    datetime DATETIME NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    fee REAL DEFAULT 0.0,
    FOREIGN KEY (trade_id) REFERENCES trades(id)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (trade_id) REFERENCES trades(id)
);
