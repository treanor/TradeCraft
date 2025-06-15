"""
Reusable filter/header bar for Trade Log and Analytics pages.
Includes symbol filter, tag filter, date picker, clear button, and quick filter buttons.
"""
from dash import dcc, html, callback, Output, Input, State, ctx
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
    Returns a filter header for the sidebar - based on the original filter_bar pattern.
    Just adds account selection and arranges vertically for sidebar layout.
    """
    symbol_options = db_access.get_all_symbols()
    tag_options = db_access.get_all_tags()
    
    return html.Div([
        # Account selection (added back)
        dbc.Row([
            dbc.Col([
                html.Label("Account:", className="form-label"),
                dcc.Dropdown(
                    id=f"{prefix}account-dropdown",
                    options=[],  # Will be populated by callback
                    placeholder="Select Account",
                    clearable=True,
                    className="mb-2"
                )
            ], width=12),
        ]),
        
        # Date range picker
        dbc.Row([
            dbc.Col([
                html.Label("Date Range:", className="form-label"),
                dcc.DatePickerRange(
                    id=f"{prefix}date-filter",
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    display_format="YYYY-MM-DD",
                    className="mb-2"
                )
            ], width=12),
        ]),
        
        # Tag and Symbol dropdowns side by side
        dbc.Row([
            dbc.Col([
                html.Label("Tags:", className="form-label"),
                dcc.Dropdown(
                    id=f"{prefix}tag-filter",
                    options=[{"label": t, "value": t} for t in tag_options],
                    placeholder="Tag",
                    multi=True,
                    clearable=True,
                    className="mb-2"
                )
            ], width=6),
            dbc.Col([
                html.Label("Symbol:", className="form-label"),
                dcc.Dropdown(
                    id=f"{prefix}symbol-filter",
                    options=[{"label": s, "value": s} for s in symbol_options],
                    placeholder="Symbol",
                    multi=True,
                    clearable=True,
                    className="mb-2"
                )
            ], width=6),
        ]),
        
        # Quick filter buttons (your original set)
        dbc.Row([
            dbc.Col([
                html.Label("Quick Filters:", className="form-label"),
                dbc.ButtonGroup([
                    dbc.Button("Today", id=f"{prefix}quickfilter-today", color="primary", outline=True, size="sm"),
                    dbc.Button("Yesterday", id=f"{prefix}quickfilter-yesterday", color="primary", outline=True, size="sm"),
                    dbc.Button("This Week", id=f"{prefix}quickfilter-thisweek", color="primary", outline=True, size="sm"),
                    dbc.Button("Last Week", id=f"{prefix}quickfilter-lastweek", color="primary", outline=True, size="sm"),
                    dbc.Button("This Month", id=f"{prefix}quickfilter-thismonth", color="primary", outline=True, size="sm"),
                    dbc.Button("Last Month", id=f"{prefix}quickfilter-lastmonth", color="primary", outline=True, size="sm"),
                    dbc.Button("All Time", id=f"{prefix}quickfilter-alltime", color="primary", outline=True, size="sm"),
                ], size="sm", className="d-flex flex-wrap gap-1"),
            ], width=12),
        ], className="mb-2"),
        
        # Clear filters button
        dbc.Row([
            dbc.Col([
                dbc.Button("Clear Filters", id=f"{prefix}clear-filters", color="secondary", outline=True, size="sm", className="w-100")
            ], width=12),
        ], className="mb-2"),
        
        # Stores
        dcc.Store(id="account-store", storage_type="local"),
    ])

def get_persistent_account() -> int | None:
    """Get the last selected account from dcc.Store (localStorage) if available."""
    store = ctx.states.get("account-store.data")
    return store if store else None

def user_account_dropdowns() -> html.Div:
    """Return a row with only account dropdown for the header (user selection is now in settings)."""
    return dbc.Row([
        dcc.Store(id="user-store", storage_type="local"),
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
        dcc.Store(id="account-store", storage_type="local"),
    ], className="g-1 align-items-center", style={"marginLeft": 16})



@callback(
    Output("account-dropdown", "options"),
    Output("account-dropdown", "value"),
    Output("account-store", "data"),
    Input("user-store", "data"),
    Input("account-dropdown", "value"),
    State("account-store", "data"),
)
def update_account_dropdown(user_id: int, account_id: int, store_account: int) -> tuple[list[dict], int | None, int | None]:
    """Update account dropdown options and value when user or account changes. Persist selection. Defaults to first account if no selection."""
    accounts = db_access.get_accounts_for_user(user_id) if user_id else []
    options = [{"label": f"{a['name']} ({a['broker']})" if a['broker'] else a['name'], "value": a["id"]} for a in accounts]
    default_value = options[0]["value"] if options else None
    value = account_id or store_account or default_value
    return options, value, value
