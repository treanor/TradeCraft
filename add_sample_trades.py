#!/usr/bin/env python3
"""
Add sample trades for a specific user account.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

def add_sample_trades_for_user(username: str, num_trades: int = 10):
    """Add sample trades for a specific user."""
    db_path = Path('data/tradecraft.db')
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get user and account info
        cursor.execute("""
            SELECT u.id, a.id, a.name 
            FROM users u 
            JOIN accounts a ON u.id = a.user_id 
            WHERE u.username = ?
            LIMIT 1
        """, (username,))
        
        result = cursor.fetchone()
        if not result:
            print(f"No user/account found for username: {username}")
            return
        
        user_id, account_id, account_name = result
        print(f"Adding {num_trades} sample trades for {username} (account: {account_name})")
        
        # Sample symbols and data
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META", "AMZN"]
        now = datetime.now()
        
        for i in range(num_trades):
            # Random trade data
            symbol = random.choice(symbols)
            trade_date = now - timedelta(days=random.randint(1, 90))
            close_date = trade_date + timedelta(hours=random.randint(1, 48))
            
            entry_price = random.uniform(50, 300)
            is_profitable = random.random() < 0.6  # 60% win rate
            exit_price = entry_price * (1 + random.uniform(0.01, 0.15)) if is_profitable else entry_price * (1 - random.uniform(0.01, 0.10))
            
            quantity = random.randint(10, 100)
            notes = f"Sample trade #{i+1} for {symbol}"
            tags = random.choice(["momentum", "swing", "earnings", "technical"])
            
            # Insert trade
            cursor.execute("""
                INSERT INTO trades (user_id, account_id, asset_symbol, asset_type, opened_at, closed_at, notes, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, account_id, symbol, "stock", 
                trade_date.isoformat(), close_date.isoformat(), 
                notes, tags, now.isoformat(), now.isoformat()
            ))
            
            trade_id = cursor.lastrowid
            
            # Insert buy leg
            cursor.execute("""
                INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id, "buy", quantity, entry_price, round(random.uniform(0.5, 2.0), 2),
                trade_date.isoformat(), "Entry", now.isoformat(), now.isoformat()
            ))
            
            # Insert sell leg
            cursor.execute("""
                INSERT INTO trade_legs (trade_id, action, quantity, price, fees, executed_at, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id, "sell", quantity, exit_price, round(random.uniform(0.5, 2.0), 2),
                close_date.isoformat(), "Exit", now.isoformat(), now.isoformat()
            ))
        
        conn.commit()
        print(f"Successfully added {num_trades} sample trades!")

if __name__ == "__main__":
    # Add sample trades for your account
    add_sample_trades_for_user("me", 15)
