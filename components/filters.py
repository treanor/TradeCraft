"""
Reusable filter/header bar for Trade Log and Analytics pages.
Includes symbol filter, tag filter, date picker, clear button, and quick filter buttons.
"""
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
from typing import List, Optional
from utils import db_access

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
    # Fetch options from DB for dropdowns
    symbol_options = db_access.get_all_symbols()
    tag_options = db_access.get_all_tags()
    return html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id=f"{prefix}symbol-filter",
                    options=[{"label": s, "value": s} for s in symbol_options],
                    placeholder=symbol_placeholder,
                    multi=False,
                    searchable=True,
                    clearable=True,
                    style={"width": "100%"},
                ),
            ], width=3),
            dbc.Col([
                dcc.Dropdown(
                    id=f"{prefix}tag-filter",
                    options=[{"label": t, "value": t} for t in tag_options],
                    placeholder=tag_placeholder,
                    multi=False,
                    searchable=True,
                    clearable=True,
                    style={"width": "100%"},
                ),
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

def user_account_dropdowns() -> html.Div:
    """Return a row with user and account dropdowns for the header."""
    # Get users and accounts from the DB
    users = db_access.get_all_users()  # returns list of dicts: [{id, username}]
    user_options = [{"label": u["username"], "value": u["id"]} for u in users]
    # Accounts will be dynamically filtered by user selection in the callback
    return dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="user-dropdown",
                options=user_options,
                value=users[0]["id"] if users else None,
                clearable=False,
                style={"minWidth": 120, "marginRight": 8},
            )
        ], width="auto"),
        dbc.Col([
            dcc.Dropdown(
                id="account-dropdown",
                options=[],  # Populated by callback
                value=None,
                clearable=False,
                style={"minWidth": 160},
                placeholder="Select Account"
            )
        ], width="auto"),
    ], className="g-1 align-items-center", style={"marginLeft": 16})

@callback(
    Output("account-dropdown", "options"),
    Output("account-dropdown", "value"),
    Input("user-dropdown", "value"),
)
def update_account_dropdown(user_id: int):
    """Update account dropdown options and value when user changes."""
    accounts = db_access.get_accounts_for_user(user_id)
    options = [{"label": f"{a['name']} ({a['broker']})" if a['broker'] else a['name'], "value": a["id"]} for a in accounts]
    value = options[0]["value"] if options else None
    return options, value
