"""
Authentication module for TradeCraft Streamlit app.

Provides login, registration, and session management functionality.
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Database path
DB_PATH = Path("data/tradecraft.db")

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, password_hash = stored_hash.split(":", 1)
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == password_hash
    except ValueError:
        return False

def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The plain text password
    
    Returns:
        User dict if authentication successful, None otherwise
    """
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = ?",
                (username,)
            )
            user_row = cursor.fetchone()
            
            if user_row and verify_password(password, user_row['password_hash']):
                return {
                    'id': user_row['id'],
                    'username': user_row['username'],
                    'email': user_row['email']
                }
    except Exception as e:
        st.error(f"Authentication error: {e}")
    
    return None

def create_user(username: str, email: str, password: str) -> bool:
    """
    Create a new user account.
    
    Args:
        username: The username
        email: The email address
        password: The plain text password
    
    Returns:
        True if user created successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                st.error("Username already exists!")
                return False
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                st.error("Email already exists!")
                return False
            
            # Create the user
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            
            st.success("Account created successfully! Please log in.")
            return True
            
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def get_user_accounts(user_id: int) -> list:
    """Get all accounts for a user."""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, broker FROM accounts WHERE user_id = ? ORDER BY name",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Error fetching accounts: {e}")
        return []

def is_logged_in() -> bool:
    """Check if user is logged in."""
    return 'user' in st.session_state and st.session_state.user is not None

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current logged-in user."""
    return st.session_state.get('user')

def logout():
    """Log out the current user."""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def show_login_form():
    """Display the login form."""
    # Custom CSS for the login form
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        font-size: 1.1rem;
        margin-bottom: 0;
        opacity: 0.8;
    }
    .demo-info {
        background: rgba(52, 152, 219, 0.1);
        border-left: 4px solid #3498db;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
    }
    .demo-info h4 {
        color: #3498db;
        margin-top: 0;
    }
    .demo-accounts {
        font-family: monospace;
        background: rgba(0, 0, 0, 0.05);
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <h1 class="login-title">📈 TradeCraft</h1>
        <p class="login-subtitle">Your Personal Trading Journal</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab1:
        st.markdown("#### Welcome Back!")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            submit_login = st.form_submit_button("🔐 Sign In", use_container_width=True)
            
            if submit_login:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Signing in..."):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.success(f"Welcome back, {user['username']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
    
    with tab2:
        st.markdown("#### Join TradeCraft")
        
        with st.form("register_form", clear_on_submit=True):
            new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            new_email = st.text_input("Email", placeholder="Enter your email", key="reg_email")
            new_password = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
            
            submit_register = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if submit_register:
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    with st.spinner("Creating account..."):
                        if create_user(new_username, new_email, new_password):
                            st.info("Account created! Please switch to the Sign In tab to log in.")
    
    # Demo accounts info
    st.markdown("""
    <div class="demo-info">
        <h4>🚀 Demo Accounts</h4>
        <p>Try these demo accounts with sample trading data:</p>
        <div class="demo-accounts">
            <strong>Username:</strong> alice<br>
            <strong>Password:</strong> password123
        </div>
        <div class="demo-accounts">
            <strong>Username:</strong> bob<br>
            <strong>Password:</strong> password123
        </div>
        <p><em>Both accounts have sample trades and analytics data for testing.</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_user_header():
    """Show logged-in user header with logout option."""
    user = get_current_user()
    if not user:
        return
    
    col1, col2, col3 = st.columns([3, 1, 1])    
    with col1:
        st.markdown(f"### 👋 Welcome, **{user['username']}**")
    
    with col2:
        # Get user's accounts count and create initial account if needed
        accounts = get_user_accounts(user['id'])
        if len(accounts) == 0:
            # Auto-create initial account for new users
            if create_initial_account(user['id'], user['username']):
                st.rerun()  # Refresh to show the new account
        st.metric("Accounts", len(accounts))
    
    with col3:
        if st.button("🚪 Logout", help="Sign out of your account"):
            logout()

def require_auth(app_function):
    """
    Decorator to require authentication for app functions.
    
    Usage:
        @require_auth
        def main_app():
            # Your app code here
    """
    def wrapper():
        if not is_logged_in():
            show_login_form()
        else:
            show_user_header()
            st.markdown("---")
            app_function()
    
    return wrapper

def get_demo_users():
    """Get or create demo users for testing."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if demo users exist
            cursor.execute("SELECT username FROM users WHERE username IN ('alice', 'bob')")
            existing_users = [row[0] for row in cursor.fetchall()]
            
            # Create missing demo users
            demo_users = [
                ('alice', 'alice@demo.com', 'password123'),
                ('bob', 'bob@demo.com', 'password123')
            ]
            
            for username, email, password in demo_users:
                if username not in existing_users:
                    password_hash = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                        (username, email, password_hash)
                    )
            
            conn.commit()
            
    except Exception as e:
        print(f"Error creating demo users: {e}")

def create_initial_account(user_id: int, username: str) -> bool:
    """Create an initial trading account for a new user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user already has accounts
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE user_id = ?", (user_id,))
            account_count = cursor.fetchone()[0]
            
            if account_count == 0:
                # Create initial account
                now = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO accounts (user_id, name, broker, account_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, f"{username}_trading_account", "Personal Broker", f"{username.upper()}-001", now, now)
                )
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Error creating initial account: {e}")
    
    return False

# Initialize demo users when module is imported
get_demo_users()
