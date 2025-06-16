# TradeCraft Authentication System

## Overview
TradeCraft now includes a secure authentication system that allows multiple users to have their own trading journals while keeping data separate and secure.

## Features

### 🔐 User Authentication
- **Secure Login**: Username/password authentication with salted password hashing
- **User Registration**: New users can create accounts 
- **Session Management**: Persistent login sessions during app usage
- **Data Isolation**: Each user sees only their own trades and accounts

### 👥 Multi-User Support
- **Personal Journals**: Each user has their own trading data
- **Multiple Accounts**: Users can have multiple trading accounts (different brokers, etc.)
- **User-Specific Analytics**: All charts and statistics are filtered to the logged-in user

### 🛡️ Security
- **Password Hashing**: Uses SHA-256 with random salts (not stored in plain text)
- **Session-Based**: Authentication persists during browser session
- **Input Validation**: Prevents SQL injection and validates user input

## How to Use

### Login
1. Run the app: `streamlit run streamlit_app.py`
2. You'll see the login screen with two tabs: "Login" and "Register"
3. Use demo credentials:
   - Username: `alice` | Password: `password123`
   - Username: `bob` | Password: `password123`

### Create New Account
1. Click the "Register" tab
2. Fill in:
   - Username (must be unique)
   - Email address
   - Password (minimum 6 characters)
   - Confirm password
3. Click "Create Account"
4. Switch to "Login" tab and sign in

### Using the App
- Once logged in, you'll see your username in the header
- The sidebar shows accounts belonging to your user
- All trades, analytics, and data are filtered to your user
- Click "Logout" to end your session

## Technical Details

### Files Added
- `auth.py` - Authentication module with login/register/session management
- `setup_demo_accounts.py` - Script to create demo accounts
- `update_demo_passwords.py` - Script to update user passwords

### Database Schema
The existing database already had the necessary tables:
- `users` - User accounts with username, email, password_hash
- `accounts` - Trading accounts linked to users
- `trades` - All trades are linked to user_id

### Code Changes
- Added `@require_auth` decorator to the main app function
- Modified `load_trades()` to filter by current user
- Modified `load_accounts()` to show only current user's accounts
- Added user header with logout button

## Security Considerations

### Password Security
- Passwords are hashed using SHA-256 with random 16-byte salts
- Original passwords are never stored in the database
- Each password gets a unique salt for added security

### Session Management
- Uses Streamlit's built-in session state
- Sessions persist during browser usage
- No persistent sessions across browser restarts (by design)

### Data Isolation
- All database queries filter by `user_id`
- Users can only see their own data
- No admin interface (add users via registration)

## Demo Data

### Demo Users
Two demo users are available:
- **alice**: Has sample trading data for testing
- **bob**: Has sample trading data for testing
- Both use password: `password123`

### Creating Demo Accounts
If you need to recreate demo accounts:
```bash
python setup_demo_accounts.py
```

### Updating Passwords
To update demo user passwords:
```bash
python update_demo_passwords.py
```

## Future Enhancements

### Possible Additions
- **Password Reset**: Email-based password reset functionality
- **User Profiles**: Extended user information and preferences
- **Admin Interface**: User management for admins
- **OAuth Integration**: Google/GitHub login support
- **Two-Factor Authentication**: SMS or app-based 2FA
- **Session Timeout**: Automatic logout after inactivity

### Database Improvements
- **User Preferences**: Store UI preferences per user
- **Audit Logging**: Track user actions and login history
- **Role-Based Access**: Different permission levels

## Troubleshooting

### Common Issues

**"No accounts found for your user"**
- Run `python setup_demo_accounts.py` to create demo accounts
- Check that the user exists in the database
- Verify accounts table has entries for your user_id

**"Invalid username or password"**
- Check that you're using the correct demo credentials
- Run `python update_demo_passwords.py` to reset demo passwords
- Verify users exist: `python check_users.py`

**Database errors**
- Ensure `data/tradecraft.db` exists
- Run `python utils/sample_data.py` to recreate sample data
- Check file permissions on database file

### Debugging
- Check Streamlit logs in the terminal
- Verify database schema with `python check_db.py`
- Test authentication functions in `auth.py` directly

## Migration from Previous Version

If you were using the app before authentication:
1. Your existing data is preserved
2. All trades are linked to user_id = 3 (hardcoded previously)
3. Demo users (alice, bob) have their own separate data
4. You can create a new user account or use demo accounts

The authentication system is fully backward compatible with existing data.
