#!/usr/bin/env python3
"""
Quick script to fix test method calls after MVVM refactoring.
Removes user_id and account_id parameters from TradeLogViewModel.get_filtered_trades_data() calls.
"""

import re

def fix_test_file(file_path):
    """Fix a test file by removing user_id and account_id parameters."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match get_filtered_trades_data calls with user_id and account_id
    pattern = r'view_model\.get_filtered_trades_data\(\s*user_id=\d+,\s*account_id=\d+,\s*'
    replacement = 'view_model.get_filtered_trades_data('
    
    content = re.sub(pattern, replacement, content)
    
    # Also fix calls with no other parameters
    pattern2 = r'view_model\.get_filtered_trades_data\(\s*user_id=[^,)]+,\s*account_id=[^,)]+\s*\)'
    replacement2 = 'view_model.get_filtered_trades_data()'
    
    content = re.sub(pattern2, replacement2, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_test_file("tests/test_integration.py")
    fix_test_file("tests/test_view_model.py")
    print("All test files fixed!")
