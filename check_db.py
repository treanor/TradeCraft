#!/usr/bin/env python3
"""
Script to check database contents for TradeCraft app
"""
import sqlite3
from pathlib import Path

def check_database():
    db_path = Path('data/tradecraft.db')
    if not db_path.exists():
        print('Database file not found at data/tradecraft.db')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Tables in database:')
        for table in tables:
            print(f'  - {table[0]}')
        print()
        
        # Check trades count
        cursor.execute('SELECT COUNT(*) FROM trades')
        trade_count = cursor.fetchone()[0]
        print(f'Trades count: {trade_count}')
        
        # Check trade_legs count
        cursor.execute('SELECT COUNT(*) FROM trade_legs')
        legs_count = cursor.fetchone()[0]
        print(f'Trade legs count: {legs_count}')
        print()
        
        # Show some trade data
        cursor.execute('SELECT id, asset_symbol, opened_at, closed_at FROM trades LIMIT 5')
        trades = cursor.fetchall()
        print('First 5 trades:')
        for trade in trades:
            print(f'  ID: {trade[0]}, Symbol: {trade[1]}, Opened: {trade[2]}, Closed: {trade[3]}')
        print()
        
        # Show some trade legs data
        cursor.execute('SELECT trade_id, action, quantity, price, fees, executed_at FROM trade_legs LIMIT 10')
        legs = cursor.fetchall()
        print('First 10 trade legs:')
        for leg in legs:
            print(f'  Trade ID: {leg[0]}, Action: {leg[1]}, Qty: {leg[2]}, Price: ${leg[3]}, Fees: ${leg[4]}, Time: {leg[5]}')
        print()
        
        # Check if legs are associated with trades
        cursor.execute('''
            SELECT t.id, t.asset_symbol, COUNT(tl.id) as leg_count
            FROM trades t
            LEFT JOIN trade_legs tl ON t.id = tl.trade_id
            GROUP BY t.id, t.asset_symbol
            LIMIT 10
        ''')
        trade_leg_counts = cursor.fetchall()
        print('Trade leg associations (first 10 trades):')
        for row in trade_leg_counts:
            print(f'  Trade ID: {row[0]}, Symbol: {row[1]}, Legs: {row[2]}')
        
    except Exception as e:
        print(f'Error querying database: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    check_database()
