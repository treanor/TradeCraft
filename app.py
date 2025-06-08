"""
TradeCraft - Personal Trading Journal and Analytics Dashboard

A comprehensive Dash application for tracking and analyzing trading performance.
Entry point for the multi-page Dash application with Bootstrap styling.

Author: TradeCraft Development Team
Version: 1.0.0
"""
from typing import Optional
import dash
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app() -> Dash:
    """
    Create and configure the main Dash application.
    
    Returns:
        Dash: Configured Dash application instance
    """
    app = dash.Dash(
        __name__,
        use_pages=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
        suppress_callback_exceptions=True,
        title="TradeCraft - Trading Journal",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
    # Set server configuration
    app.server.secret_key = os.getenv('SECRET_KEY', 'tradecraft-dev-key')
    
    return app

# Initialize the Dash app
app: Dash = create_app()

# Import pages to register them (must be after app creation)
import pages.dashboard
import pages.trades  
import pages.analytics
import pages.settings

def create_navigation() -> dbc.NavbarSimple:
    """
    Create the main navigation bar for the application.
    
    Returns:
        dbc.NavbarSimple: Bootstrap navigation component
    """
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Trade Log", href="/trades", active="exact")),
            dbc.NavItem(dbc.NavLink("Analytics", href="/analytics", active="exact")),
            dbc.NavItem(dbc.NavLink("Settings", href="/settings", active="exact")),
        ],
        brand="TradeCraft",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    )

# App layout with navigation
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    
    # Header navigation
    create_navigation(),
    
    # Page content
    dash.page_container
], fluid=True)


def main() -> None:
    """
    Main entry point for the application.
    Reads configuration from environment variables and starts the server.
    """
    debug_mode: bool = os.getenv("DEBUG", "True").lower() == "true"
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8050"))
    
    print(f"Starting TradeCraft application on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    
    app.run_server(debug=debug_mode, host=host, port=port)


if __name__ == "__main__":
    main()
