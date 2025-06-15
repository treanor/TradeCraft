"""
Analytics Page Module

Main module for the analytics functionality.
Follows MVVM pattern with clean separation of concerns.
"""
from .layout import create_analytics_layout
from .callbacks import register_analytics_callbacks

# Create the layout
layout = create_analytics_layout()

# Register all callbacks
register_analytics_callbacks()
