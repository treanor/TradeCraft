"""
Database access utilities for Trade Craft.

Provides type-annotated functions for querying and manipulating trades and trade legs.
"""

import sqlite3
from pathlib import Path
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime
import logging
from contextlib import contextmanager
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("data/tradecraft.db")

class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass

@dataclass
class TradeAnalytics:
    """Data class for trade analytics results."""
    trade_id: int
    total_bought: int
    total_sold: int
    avg_buy_price: float
    avg_sell_price: float
    total_fees: float
    realized_pnl: float
    open_qty: int
    status: str
    closed_at: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics."""
    total_trades: int
    win_count: int
    loss_count: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    total_pnl: float
    max_drawdown: float
    expectancy: float

@contextmanager
def get_connection(db_path: Path = DB_PATH):
    """
    Context manager for database connections with proper error handling.
    Args:
        db_path: Path to the SQLite database file.
    Yields:
        sqlite3.Connection object.
    """
    conn = None
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Database operation failed: {e}")
    finally:
        if conn:
            conn.close()

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

def fetch_trades_for_user_and_account(
    user_id: Optional[int], 
    account_id: Optional[int], 
    db_path: Path = DB_PATH
) -> List[Dict[str, Any]]:
    """
    Fetch all trades for a given user_id and account_id.
    Args:
        user_id: The user ID (can be None for empty results).
        account_id: The account ID (can be None for empty results).
        db_path: Path to the SQLite database file.
    Returns:
        List of trade dictionaries.
    """
    if user_id is None or account_id is None:
        return []
    
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trades
            WHERE user_id = ? AND account_id = ?
            ORDER BY opened_at DESC
        ''', (user_id, account_id))
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
            SELECT 
                SUM(CASE WHEN action IN ('buy', 'buy to open') THEN quantity ELSE 0 END) -
                SUM(CASE WHEN action IN ('sell', 'sell to close') THEN quantity ELSE 0 END) as net_qty
            FROM trade_legs
            WHERE trade_id = ?
        ''', (trade_id,))
        result = cur.fetchone()
        return (result[0] or 0) > 0

def insert_trade(
    user_id: int, 
    asset_symbol: Union[str, List[str]], 
    asset_type: str, 
    opened_at: str, 
    notes: str = "", 
    tags: Union[str, List[str]] = "", 
    account_id: Optional[int] = None,
    db_path: Path = DB_PATH
) -> int:
    """
    Insert a new trade and return its ID.
    Args:
        user_id: The user ID for the trade.
        asset_symbol: The asset symbol (string or list).
        asset_type: The asset type.
        opened_at: ISO datetime string for when the trade was opened.
        notes: Optional notes for the trade.
        tags: Optional tags for the trade (comma-separated string or list).
        account_id: The account ID for the trade.
        db_path: Path to the SQLite database file.
    Returns:
        The new trade's ID.
    """
    if account_id is None:
        # Get default account for user
        accounts = get_accounts_for_user(user_id, db_path)
        if not accounts:
            raise DatabaseError(f"No accounts found for user {user_id}")
        account_id = accounts[0]["id"]
    
    now = datetime.now().isoformat()
    symbol_str = asset_symbol if isinstance(asset_symbol, str) else ",".join(asset_symbol)
    tags_str = tags if isinstance(tags, str) else ",".join(tags)
    
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trades (user_id, account_id, asset_symbol, asset_type, opened_at, notes, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, account_id, symbol_str, asset_type, opened_at, notes, tags_str, now, now))
        trade_id = cur.lastrowid
        
        # Insert tags into tags/trade_tags tables
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
        
        # Insert symbols into symbols/trade_symbols tables
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

def insert_trade_leg(
    trade_id: int, 
    action: str, 
    quantity: int, 
    price: float, 
    fees: float, 
    executed_at: str, 
    notes: str = "", 
    db_path: Path = DB_PATH
) -> int:
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
        
        leg_id = cur.lastrowid
        
        # Check if trade is now closed and update closed_at
        if not is_trade_open(trade_id, db_path):
            # Trade is closed, set closed_at if not already set
            cur.execute('SELECT closed_at FROM trades WHERE id = ?', (trade_id,))
            closed_at_val = cur.fetchone()
            if closed_at_val and closed_at_val[0] is None:
                # Find latest executed_at of any closing leg
                cur.execute('''
                    SELECT MAX(executed_at) FROM trade_legs 
                    WHERE trade_id = ? AND action IN ("sell", "sell to close")
                ''', (trade_id,))
                last_close = cur.fetchone()[0]
                if last_close:
                    cur.execute('UPDATE trades SET closed_at = ? WHERE id = ?', (last_close, trade_id))
        
        conn.commit()
        return leg_id

def trade_analytics(trade_id: int, db_path: Path = DB_PATH) -> TradeAnalytics:
    """
    Calculate analytics for a trade: total P&L, average price, total fees, and open/closed status.
    Args:
        trade_id: The trade ID to analyze.
        db_path: Path to the SQLite database file.
    Returns:
        TradeAnalytics dataclass with calculated metrics.
    """
    legs = fetch_legs_for_trade(trade_id, db_path)
    
    if not legs:
        return TradeAnalytics(
            trade_id=trade_id,
            total_bought=0,
            total_sold=0,
            avg_buy_price=0.0,
            avg_sell_price=0.0,
            total_fees=0.0,
            realized_pnl=0.0,
            open_qty=0,
            status="empty",
            closed_at=None,
        )
    
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
    
    # Get closed_at from the latest sell leg if trade is closed
    closed_at = None
    if status == "closed":
        sell_legs = [l for l in legs if l['action'] in ("sell", "sell to close")]
        if sell_legs:
            closed_at = max(sell_legs, key=lambda x: x['executed_at'])['executed_at']
    
    return TradeAnalytics(
        trade_id=trade_id,
        total_bought=total_bought,
        total_sold=total_sold,
        avg_buy_price=avg_buy_price,
        avg_sell_price=avg_sell_price,
        total_fees=total_fees,
        realized_pnl=realized_pnl,
        open_qty=open_qty,
        status=status,
        closed_at=closed_at,
    )

def get_tags_for_trade(trade_id: int, db_path: Path = DB_PATH) -> List[str]:
    """Return a list of tag names for a given trade."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT tags.name FROM tags
            JOIN trade_tags ON tags.id = trade_tags.tag_id
            WHERE trade_tags.trade_id = ?
            ORDER BY tags.name
        ''', (trade_id,))
        return [row[0] for row in cur.fetchall()]

def get_all_tags(db_path: Path = DB_PATH) -> List[str]:
    """Return all unique tag names in the system."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name FROM tags ORDER BY name')
        return [row[0] for row in cur.fetchall()]

def set_tags_for_trade(trade_id: int, tags: List[str], db_path: Path = DB_PATH) -> None:
    """Set the tags for a trade, replacing any existing tags."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        # Remove existing
        cur.execute('DELETE FROM trade_tags WHERE trade_id = ?', (trade_id,))
        # Insert new tags
        for tag in tags:
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
        conn.commit()

def get_symbols_for_trade(trade_id: int, db_path: Path = DB_PATH) -> List[str]:
    """Return a list of symbols for a given trade."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT symbols.symbol FROM symbols
            JOIN trade_symbols ON symbols.id = trade_symbols.symbol_id
            WHERE trade_symbols.trade_id = ?
            ORDER BY symbols.symbol
        ''', (trade_id,))
        return [row[0] for row in cur.fetchall()]

def get_all_symbols(db_path: Path = DB_PATH) -> List[str]:
    """Return all unique symbols in the system."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT symbol FROM symbols ORDER BY symbol')
        return [row[0] for row in cur.fetchall()]

def set_symbols_for_trade(trade_id: int, symbols: List[str], db_path: Path = DB_PATH) -> None:
    """Set the symbols for a trade, replacing any existing symbols."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        # Remove existing
        cur.execute('DELETE FROM trade_symbols WHERE trade_id = ?', (trade_id,))
        # Insert new symbols
        for symbol in symbols:
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

def get_all_users(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Return all users as a list of dicts with id and username."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM users ORDER BY username')
        return [{"id": row[0], "username": row[1]} for row in cur.fetchall()]

def get_accounts_for_user(user_id: Optional[int], db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Return all accounts for a user as a list of dicts with id, name, broker."""
    if user_id is None:
        return []
    
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name, broker FROM accounts WHERE user_id = ? ORDER BY name', (user_id,))
        return [{"id": row[0], "name": row[1], "broker": row[2]} for row in cur.fetchall()]

def get_performance_metrics(
    user_id: Optional[int], 
    account_id: Optional[int], 
    db_path: Path = DB_PATH
) -> PerformanceMetrics:
    """
    Calculate comprehensive performance metrics for a user/account.
    Returns metrics like Sharpe ratio, max drawdown, win rate, etc.
    """
    if user_id is None or account_id is None:
        return PerformanceMetrics(
            total_trades=0, win_count=0, loss_count=0, win_rate=0.0,
            avg_win=0.0, avg_loss=0.0, profit_factor=0.0, total_pnl=0.0,
            max_drawdown=0.0, expectancy=0.0
        )
    
    trades = fetch_trades_for_user_and_account(user_id, account_id, db_path)
    if not trades:
        return PerformanceMetrics(
            total_trades=0, win_count=0, loss_count=0, win_rate=0.0,
            avg_win=0.0, avg_loss=0.0, profit_factor=0.0, total_pnl=0.0,
            max_drawdown=0.0, expectancy=0.0
        )
    
    # Calculate basic metrics
    closed_trades = []
    for trade in trades:
        analytics = trade_analytics(trade["id"], db_path)
        if analytics.status == "closed":
            closed_trades.append(analytics)
    
    if not closed_trades:
        return PerformanceMetrics(
            total_trades=0, win_count=0, loss_count=0, win_rate=0.0,
            avg_win=0.0, avg_loss=0.0, profit_factor=0.0, total_pnl=0.0,
            max_drawdown=0.0, expectancy=0.0
        )
    
    pnls = [t.realized_pnl for t in closed_trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    
    total_trades = len(closed_trades)
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    profit_factor = abs(sum(wins) / sum(losses)) if losses and sum(losses) != 0 else float('inf')
    
    # Calculate max drawdown
    cumulative_pnl = []
    running_total = 0
    for pnl in pnls:
        running_total += pnl
        cumulative_pnl.append(running_total)
    
    max_drawdown = 0
    peak = cumulative_pnl[0] if cumulative_pnl else 0
    for value in cumulative_pnl:
        if value > peak:
            peak = value
        drawdown = peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return PerformanceMetrics(
        total_trades=total_trades,
        win_count=win_count,
        loss_count=loss_count,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        profit_factor=profit_factor,
        total_pnl=sum(pnls),
        max_drawdown=max_drawdown,
        expectancy=sum(pnls) / len(pnls) if pnls else 0,
    )

def delete_trade(trade_id: int, db_path: Path = DB_PATH) -> bool:
    """
    Delete a trade and all its associated legs, tags, and symbols.
    Args:
        trade_id: The trade ID to delete.
        db_path: Path to the SQLite database file.
    Returns:
        True if successful, False otherwise.
    """
    try:
        with get_connection(db_path) as conn:
            cur = conn.cursor()
            # Delete in correct order due to foreign key constraints
            cur.execute('DELETE FROM trade_legs WHERE trade_id = ?', (trade_id,))
            cur.execute('DELETE FROM trade_tags WHERE trade_id = ?', (trade_id,))
            cur.execute('DELETE FROM trade_symbols WHERE trade_id = ?', (trade_id,))
            cur.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to delete trade {trade_id}: {e}")
        return False

def update_trade(
    trade_id: int, 
    notes: Optional[str] = None, 
    tags: Optional[List[str]] = None,
    db_path: Path = DB_PATH
) -> bool:
    """
    Update trade notes and/or tags.
    Args:
        trade_id: The trade ID to update.
        notes: New notes (if provided).
        tags: New tags list (if provided).
        db_path: Path to the SQLite database file.
    Returns:
        True if successful, False otherwise.
    """
    try:
        with get_connection(db_path) as conn:
            cur = conn.cursor()
            
            if notes is not None:
                cur.execute(
                    'UPDATE trades SET notes = ?, updated_at = ? WHERE id = ?',
                    (notes, datetime.now().isoformat(), trade_id)
                )
            
            if tags is not None:
                set_tags_for_trade(trade_id, tags, db_path)
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to update trade {trade_id}: {e}")
        return False

def get_trade_count_by_status(user_id: int, account_id: int, db_path: Path = DB_PATH) -> Dict[str, int]:
    """Get count of trades by status (open/closed) for quick stats."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT 
                CASE WHEN closed_at IS NULL THEN 'open' ELSE 'closed' END as status,
                COUNT(*) as count
            FROM trades 
            WHERE user_id = ? AND account_id = ?
            GROUP BY status
        ''', (user_id, account_id))
        return {row[0]: row[1] for row in cur.fetchall()}

def get_recent_trades(
    user_id: int, 
    account_id: int, 
    limit: int = 10, 
    db_path: Path = DB_PATH
) -> List[Dict[str, Any]]:
    """Get the most recent trades for quick display."""
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM trades
            WHERE user_id = ? AND account_id = ?
            ORDER BY opened_at DESC
            LIMIT ?
        ''', (user_id, account_id, limit))
        return [dict(row) for row in cur.fetchall()]