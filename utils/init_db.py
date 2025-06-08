"""
Initialize the SQLite database for TradeCraft using the schema.sql file.
Run this script once to create all tables in data/tradecraft.db.
"""
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path("data/schema.sql")
DB_PATH = Path("data/tradecraft.db")

def init_db(schema_path: Path = SCHEMA_PATH, db_path: Path = DB_PATH) -> None:
    """
    Initialize the SQLite database using the provided schema file.
    Args:
        schema_path: Path to the SQL schema file.
        db_path: Path to the SQLite database file.
    """
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    sql = schema_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
    print(f"Database initialized at {db_path}.")

if __name__ == "__main__":
    init_db()
