#!/usr/bin/env python3
"""
Setup demo accounts for existing users to ensure login works properly.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def setup_demo_accounts():
    """Create demo accounts for alice and bob if they don't exist."""
    db_path = Path('data/tradecraft.db')
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get user IDs
        cursor.execute("SELECT id, username FROM users WHERE username IN ('alice', 'bob')")
        users = cursor.fetchall()
        
        if not users:
            print("No demo users found. Please run sample_data.py first.")
            return
        
        now = datetime.now().isoformat()
        
        for user_id, username in users:
            # Check if accounts already exist
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE user_id = ?", (user_id,))
            account_count = cursor.fetchone()[0]
            
            if account_count == 0:
                # Create demo accounts
                accounts = [
                    (user_id, f"{username}_demo_account", "DemoBreker", f"{username.upper()}-001", now, now),
                    (user_id, f"{username}_trading_account", "TradeBroker", f"{username.upper()}-002", now, now),
                ]
                
                cursor.executemany(
                    "INSERT INTO accounts (user_id, name, broker, account_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    accounts
                )
                print(f"Created demo accounts for {username}")
            else:
                print(f"Accounts already exist for {username}")
        
        conn.commit()
        print("Demo account setup complete!")

if __name__ == "__main__":
    setup_demo_accounts()
