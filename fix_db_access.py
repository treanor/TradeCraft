import re

# Read the file
with open('utils/db_access.py', 'r') as f:
    content = f.read()

# Replace all occurrences of 'db_path: Path = DB_PATH' with 'db_path: Optional[Path] = None'
content = re.sub(r'db_path: Path = DB_PATH', r'db_path: Optional[Path] = None', content)

# Add db_path = get_db_path() check at the beginning of functions that need it
functions_to_fix = [
    'fetch_trades_for_user_and_account',
    'fetch_legs_for_trade', 
    'is_trade_open',
    'insert_trade',
    'insert_trade_leg',
    'trade_analytics',
    'get_tags_for_trade',
    'get_all_tags',
    'set_tags_for_trade',
    'get_symbols_for_trade',
    'get_all_symbols',
    'set_symbols_for_trade',
    'get_all_users',
    'get_accounts_for_user'
]

for func_name in functions_to_fix:
    # Pattern to match function definition and first line of function body
    pattern = rf'(def {func_name}\([^)]+\) -> [^:]+:\s*"""[^"]*""")\s*(\n\s+)(with get_connection\(db_path\)|conn = get_connection\(db_path\)|[a-z_]+ = [^=\n]+)'
    replacement = r'\1\2if db_path is None:\2    db_path = get_db_path()\2\3'
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Write the file back
with open('utils/db_access.py', 'w') as f:
    f.write(content)

print("Fixed db_access.py function signatures")
