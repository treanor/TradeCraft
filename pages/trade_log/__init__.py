"""
Trade Log Page Module

Main module for the trade log functionality.
Follows MVVM pattern with clean separation of concerns.
"""
from .layout import create_trade_log_layout
from .callbacks import register_trade_log_callbacks

# Create the layout
layout = create_trade_log_layout()

# Register all callbacks
register_trade_log_callbacks()
