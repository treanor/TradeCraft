"""
Configuration management for Trade Craft.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: Path
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7

@dataclass
class AppConfig:
    """Application configuration settings."""
    debug: bool
    host: str
    port: int
    title: str
    theme: str
    timezone: str

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.database = DatabaseConfig(
            path=Path(os.getenv("DB_PATH", "data/tradecraft.db")),
            backup_enabled=os.getenv("DB_BACKUP_ENABLED", "true").lower() == "true",
            backup_interval_hours=int(os.getenv("DB_BACKUP_INTERVAL", "24")),
            max_backups=int(os.getenv("DB_MAX_BACKUPS", "7"))
        )
        
        self.app = AppConfig(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8050")),
            title=os.getenv("APP_TITLE", "Trade Craft Journal"),
            theme=os.getenv("THEME", "bootstrap"),
            timezone=os.getenv("TIMEZONE", "UTC")
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.debug
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.app.debug

# Global config instance
config = Config()