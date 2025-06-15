#!/usr/bin/env python3
"""
Check users and accounts in the database
"""
from utils.db_access import get_all_users

def get_all_accounts():
    """Get all accounts from database"""
    import sqlite3
    from pathlib import Path
    
    db_path = Path('data/tradecraft.db')
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts')
        return [dict(row) for row in cursor.fetchall()]

def check_users_accounts():
    users = get_all_users()
    print('Users in database:')
    for user in users:
        print(f'  ID: {user["id"]}, Username: {user["username"]}')

    print()
    accounts = get_all_accounts()
    print('Accounts in database:')
    for account in accounts:
        print(f'  ID: {account["id"]}, User ID: {account["user_id"]}, Name: {account["name"]}')

if __name__ == '__main__':
    check_users_accounts()
