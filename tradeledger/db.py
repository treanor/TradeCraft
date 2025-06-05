import sqlite3
from typing import Optional
import pandas as pd

DB_NAME = "trades.db"


def init_db(db_name: str = DB_NAME) -> None:
    """Initialize the SQLite database and create the trades table if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            side TEXT,
            quantity REAL,
            price REAL,
            pnl REAL,
            notes TEXT,
            tags TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_connection(db_name: str = DB_NAME) -> sqlite3.Connection:
    return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)


def add_trade(date: str, ticker: str, side: str, quantity: float, price: float, pnl: float,
              notes: str = "", tags: str = "", db_name: str = DB_NAME) -> None:
    conn = get_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trades (date, ticker, side, quantity, price, pnl, notes, tags)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (date, ticker, side, quantity, price, pnl, notes, tags)
    )
    conn.commit()
    conn.close()


def update_trade(trade_id: int, date: str, ticker: str, side: str, quantity: float,
                 price: float, pnl: float, notes: str = "", tags: str = "",
                 db_name: str = DB_NAME) -> None:
    conn = get_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE trades SET date=?, ticker=?, side=?, quantity=?, price=?, pnl=?,
        notes=?, tags=? WHERE id=?
        """,
        (date, ticker, side, quantity, price, pnl, notes, tags, trade_id)
    )
    conn.commit()
    conn.close()


def delete_trade(trade_id: int, db_name: str = DB_NAME) -> None:
    conn = get_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()


def fetch_trades(db_name: str = DB_NAME) -> pd.DataFrame:
    conn = get_connection(db_name)
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY date DESC", conn,
                           parse_dates=["date"])
    conn.close()
    return df
