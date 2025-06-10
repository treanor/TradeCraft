"""
Trade Craft Dash App Entry Point

- Multi-page support using dash.page_registry
- Basic navigation bar and layout
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import importlib
import os

# Register pages from the /pages directory automatically
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Trade Craft Journal"
)

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Trade Log", href="/trade_log", className="nav-link")),
        dbc.NavItem(dcc.Link("Analytics", href="/analytics", className="nav-link")),
        dbc.NavItem(dcc.Link("Calendar", href="/calendar", className="nav-link")),
    ],
    brand="Trade Craft",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)

# App layout with navigation and page container
app.layout = dbc.Container([
    navbar,
    dash.page_container
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
