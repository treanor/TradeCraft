#!/usr/bin/env python3
"""
Update demo users with proper password hashes for login testing.
"""

import sqlite3
from pathlib import Path
from auth import hash_password

def update_demo_passwords():
    """Update alice and bob with hashed passwords."""
    db_path = Path('data/tradecraft.db')
    
    demo_users = [
        ('alice', 'password123'),
        ('bob', 'password123')
    ]
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for username, password in demo_users:
            # Check if user exists
            cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            
            if user_row:
                user_id, current_hash = user_row
                
                # Update password hash if it's not properly formatted
                if not current_hash or ':' not in current_hash:
                    new_hash = hash_password(password)
                    cursor.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (new_hash, user_id)
                    )
                    print(f"Updated password hash for {username}")
                else:
                    print(f"Password already properly hashed for {username}")
            else:
                print(f"User {username} not found")
        
        conn.commit()
        print("Password update complete!")

if __name__ == "__main__":
    update_demo_passwords()
