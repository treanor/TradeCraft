"""
Reusable filter/header bar for Trade Log and Analytics pages.
Includes symbol filter, tag filter, date picker, clear button, and quick filter buttons.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from typing import List, Optional

def filter_bar(
    tag_options: List[str],
    symbol_options: List[str],
    prefix: str = ""
) -> html.Div:
    """
    Returns a filter bar Div with date picker, tag filter, symbol filter, quick filter buttons, and clear filter button.
    prefix: Optional string to prefix component IDs for uniqueness per page.
    """
    return dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id=f"{prefix}date-filter",
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                display_format="YYYY-MM-DD",
                className="mb-2"
            )
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id=f"{prefix}tag-filter",
                options=[{"label": t, "value": t} for t in tag_options],
                placeholder="Tag",
                multi=True,
                clearable=True,
                className="mb-2"
            )
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id=f"{prefix}symbol-filter",
                options=[{"label": s, "value": s} for s in symbol_options],
                placeholder="Symbol",
                multi=True,
                clearable=True,
                className="mb-2"
            )
        ], width=2),
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Today", id=f"{prefix}quickfilter-today", color="primary", outline=True, size="sm"),
                dbc.Button("This Week", id=f"{prefix}quickfilter-thisweek", color="primary", outline=True, size="sm"),
                dbc.Button("This Month", id=f"{prefix}quickfilter-thismonth", color="primary", outline=True, size="sm"),
                dbc.Button("All Time", id=f"{prefix}quickfilter-alltime", color="primary", outline=True, size="sm"),
            ], size="sm"),
        ], width=4, className="d-flex align-items-end justify-content-end"),
        dbc.Col([
            dbc.Button("Clear Filters", id=f"{prefix}clear-filters", color="secondary", outline=True, size="sm", className="ms-2")
        ], width=1, className="d-flex align-items-end justify-content-end"),
    ], className="mb-3 g-2")

def filter_header(
    symbol_placeholder: str = "Filter by symbol",
    tag_placeholder: str = "Filter by tag",
    prefix: str = "",
    show_add_trade: bool = False
) -> html.Div:
    """
    Returns a filter/header bar Div with symbol filter, tag filter, date picker, clear button, quick filter buttons, and optional Add Trade button.
    prefix: Optional string to prefix component IDs for uniqueness per page.
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Input(id=f"{prefix}symbol-filter", placeholder=symbol_placeholder, type="text", debounce=True),
            ], width=3),
            dbc.Col([
                dbc.Input(id=f"{prefix}tag-filter", placeholder=tag_placeholder, type="text", debounce=True),
            ], width=3),
            dbc.Col([
                dcc.DatePickerRange(
                    id=f"{prefix}date-filter",
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    display_format="YYYY-MM-DD"
                ),
            ], width=4),
            dbc.Col([
                dbc.Button("Clear Filters", id=f"{prefix}clear-filters", color="secondary", outline=True, className="me-2"),
            ], width=2),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("Today", id=f"{prefix}quickfilter-today", color="primary", outline=True, size="sm"),
                    dbc.Button("Yesterday", id=f"{prefix}quickfilter-yesterday", color="primary", outline=True, size="sm"),
                    dbc.Button("This Week", id=f"{prefix}quickfilter-thisweek", color="primary", outline=True, size="sm"),
                    dbc.Button("Last Week", id=f"{prefix}quickfilter-lastweek", color="primary", outline=True, size="sm"),
                    dbc.Button("This Month", id=f"{prefix}quickfilter-thismonth", color="primary", outline=True, size="sm"),
                    dbc.Button("Last Month", id=f"{prefix}quickfilter-lastmonth", color="primary", outline=True, size="sm"),
                    dbc.Button("All Time", id=f"{prefix}quickfilter-alltime", color="primary", outline=True, size="sm"),
                ], size="sm", className="mb-2"),
            ], width=10),
            dbc.Col([
                dbc.Button("Add Trade", id=f"{prefix}add-trade-btn", color="success", outline=False, className="mb-2", n_clicks=0) if show_add_trade else None,
            ], width=2, className="d-flex align-items-end justify-content-end"),
        ], className="mb-2"),
    ])
