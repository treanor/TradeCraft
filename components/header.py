"""
Header component for TradeCraft Dash app.
Follows modern neon/dark UI design and project coding standards.
"""
from dash import html, dcc
from typing import Any

def Header() -> Any:
    """
    Returns the styled header for the TradeCraft app, including app name and navigation links.
    """
    return html.Header(
        [
            html.Div([
                html.Span("TradeCraft", className="app-name"),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Nav(
                [
                    dcc.Link("Trade Log", href="/", className="nav-link"),
                    dcc.Link("Analytics", href="/analytics", className="nav-link"),
                    dcc.Link("Calendar", href="/calendar", className="nav-link"),
                ],
                style={"marginLeft": "auto", "display": "flex", "alignItems": "center"},
            ),
        ],
        className="header",
        style={"position": "relative", "zIndex": 10, "display": "flex", "alignItems": "center"},
    )
