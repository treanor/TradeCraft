"""
Reusable stat card component for TradeCraft Dash app.
"""
from dash import html
import dash_bootstrap_components as dbc


def stat_card(title: str, value: str) -> dbc.Card:
    """
    Return a styled stat card for summary statistics.

    Args:
        title (str): The label/title of the stat.
        value (str): The value to display.

    Returns:
        dbc.Card: Dash Bootstrap Card component.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div(title, className="small text-muted mb-1"),
            html.H4(value, className="mb-0")
        ])
    ], className="shadow-sm bg-dark text-light", style={"minWidth": 140, "marginRight": 12, "marginBottom": 12})
