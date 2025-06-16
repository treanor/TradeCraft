"""
Configuration management for TradeCraft application.

Handles environment variables and application settings.
"""
import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

# Database configuration
DB_PATH = Path(os.getenv("DB_PATH", os.getenv("DATABASE_PATH", "data/tradecraft.db")))

# Application configuration
DEFAULT_USER = os.getenv("DEFAULT_USER", "alice")
DEBUG_MODE = os.getenv("DEBUG", "True").lower() == "true"

# UI configuration
APP_TITLE = os.getenv("APP_TITLE", "TradeCraft Trading Journal")

def get_db_path() -> Path:
    """Get the database path from configuration."""
    return DB_PATH

def get_default_user() -> str:
    """Get the default username from configuration."""
    return DEFAULT_USER

def is_debug_mode() -> bool:
    """Check if application is running in debug mode."""
    return DEBUG_MODE
