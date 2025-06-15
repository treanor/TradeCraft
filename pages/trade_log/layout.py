"""
Trade Log Layout Module

Defines the UI layout for the trade log page.
This is the View layer in MVVM pattern - purely presentational.
"""
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def create_trade_log_layout() -> html.Div:
    """
    Create and return the complete trade log page layout.
    
    Returns:
        html.Div: The complete trade log page layout
    """
    return html.Div([        # Header section with account dropdown and stats
        _create_header_section(),
        
        # Equity curve chart
        _create_equity_chart_section(),
        
        # Trade table
        _create_trade_table_section(),
        
        # Navigation and FAB
        *_create_navigation_elements(),
        
        # Add trade modal
        _create_add_trade_modal(),
    ])


def _create_header_section() -> html.Div:
    """Create the header section with just summary stats - filtering is in the sidebar."""
    return html.Div(
        [
            html.Div(
                id="trade-log-summary-stats", 
                className="stats", 
                style={
                    "marginLeft": "auto", 
                    "maxWidth": "420px", 
                    "flex": "0 0 420px"
                }
            ),
        ],
        className="d-flex align-items-start justify-content-end",
        style={
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "flex-start",
            "justifyContent": "flex-end",
            "marginBottom": "18px",
            "gap": "18px",
            "width": "100%"
        },
    )


def _create_equity_chart_section() -> html.Div:
    """Create the equity curve chart section."""
    return html.Div([
        dcc.Graph(
            id="equity-curve-chart", 
            config={"displayModeBar": False}, 
            style={
                "background": "#23273A", 
                "borderRadius": "16px", 
                "boxShadow": "0 2px 16px #00FFCC33", 
                "padding": "12px"
            }
        ),
    ], className="card", style={"marginBottom": "24px"})


def _create_trade_table_section() -> html.Div:
    """Create the trade table section."""
    return html.Div([
        dash_table.DataTable(
            id="trade-table",
            columns=_get_table_columns(),
            data=[],
            page_size=20,
            style_table={
                "overflowX": "auto", 
                "background": "#23273A", 
                "borderRadius": "16px"
            },
            style_cell={
                "textAlign": "left", 
                "background": "#23273A", 
                "color": "#F6F8FA", 
                "border": "none", 
                "fontSize": "1.05rem"
            },
            style_header={
                "background": "#181C25", 
                "color": "#00FFCC", 
                "fontWeight": "bold", 
                "borderBottom": "2px solid #00FFCC"
            },            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#222436"},
                {"if": {"column_id": "status", "filter_query": '{status} = "WIN"'}, "color": "#00FFCC", "fontWeight": "bold"},
                {"if": {"column_id": "status", "filter_query": '{status} = "LOSS"'}, "color": "#FF4C6A", "fontWeight": "bold"},
                {"if": {"column_id": "status", "filter_query": '{status} = "OPEN"'}, "color": "#FFA500", "fontWeight": "bold"},
                {"if": {"column_id": "status", "filter_query": '{status} = "BREAK-EVEN"'}, "color": "#FFFF00", "fontWeight": "bold"},
                {"if": {"state": "selected"}, "backgroundColor": "#1AA9E5", "color": "#fff"},
            ],
            row_selectable="single",
            selected_rows=[],
            tooltip_data=[],
            tooltip_duration=None,
            markdown_options={"link_target": None},
        ),
    ], className="card", style={"marginBottom": "24px"})


def _get_table_columns() -> list:
    """Define the table columns configuration."""
    return [
        {"name": "Date", "id": "date"},
        {"name": "Symbol", "id": "symbol"},
        {"name": "Status", "id": "status"},
        {"name": "Quantity", "id": "quantity"},
        {"name": "Entry Price", "id": "entry_price", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Exit Price", "id": "exit_price", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Hold Time", "id": "hold_time"},
        {"name": "Return $", "id": "return_dollar", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Return %", "id": "return_pct", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Notes", "id": "notes_icon", "presentation": "markdown"},
        {"name": "Tags", "id": "tags_icon", "presentation": "markdown"},
    ]


def _create_navigation_elements() -> list:
    """Create navigation and floating action button elements."""
    return [
        dcc.Location(id="trade-log-navigate", refresh=True),
        html.Button("+", id="add-trade-btn", className="fab", title="Add Trade"),
    ]


def _create_add_trade_modal() -> dbc.Modal:
    """Create the add trade modal dialog."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add New Trade")),
        dbc.ModalBody([
            dbc.Form([
                _create_trade_form_fields(),
                html.Hr(className="my-3"),
                _create_legs_section(),
            ]),
        ], style={"paddingTop": "18px", "paddingBottom": "0"}),
        dbc.ModalFooter([
            dbc.Button(
                "Save", 
                id="add-trade-submit", 
                color="success", 
                className="me-2", 
                style={"fontSize": "1.1rem", "padding": "8px 24px"}
            ),
            dbc.Button(
                "Cancel", 
                id="add-trade-cancel", 
                color="secondary", 
                style={"fontSize": "1.1rem", "padding": "8px 24px"}
            ),
        ]),
    ], id="add-trade-modal", is_open=False, size="xl", style={"minWidth": "900px", "maxWidth": "1200px"})


def _create_trade_form_fields() -> dbc.Row:
    """Create the trade form input fields."""
    return dbc.Row([
        dbc.Col([
            dbc.Label("Market", className="mb-1"),
            dbc.Select(
                id="add-market",
                options=[
                    {"label": "Stock", "value": "stock"},
                    {"label": "Option", "value": "option"},
                    {"label": "Future", "value": "future"},
                    {"label": "Crypto", "value": "crypto"},
                    {"label": "Forex", "value": "forex"},
                    {"label": "Other", "value": "other"},
                ],
                value="stock",
                style={"width": "100%", "fontSize": "1.05rem"}
            ),
        ], width=2, style={"maxWidth": "160px", "flex": "0 0 160px", "paddingRight": "32px"}),
        dbc.Col([
            dbc.Label("Symbol", className="mb-1"),
            dbc.Input(
                id="add-symbol", 
                type="text", 
                required=True, 
                style={"width": "100%", "fontSize": "1.05rem"}
            ),
        ], width=2, style={"maxWidth": "160px", "flex": "0 0 160px", "paddingRight": "32px"}),
        dbc.Col([
            dbc.Label("Journal/Notes", className="mb-1"),
            dbc.Textarea(
                id="add-notes", 
                placeholder="Optional notes...", 
                style={"width": "100%", "height": 38, "fontSize": "1.05rem"}
            ),
        ], width=8, style={"minWidth": "320px", "flex": "1 1 320px"}),
    ], className="mb-3 g-3 align-items-end flex-nowrap", style={"flexWrap": "nowrap", "display": "flex"})


def _create_legs_section() -> list:
    """Create the legs section of the modal."""
    return [
        html.H5("Legs", className="mb-3 mt-3"),
        html.Div(
            id="add-legs-table",
            style={
                "background": "#fff",
                "border": "1px solid #e2e3e5",
                "borderRadius": "12px",
                "padding": "18px 18px 10px 18px",
                "marginBottom": "18px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
            }
        ),
        dbc.Row([
            dbc.Col([], width=9),
            dbc.Col([
                dbc.Button(
                    "+", 
                    id="add-leg-btn", 
                    color="primary", 
                    outline=True, 
                    className="my-2", 
                    size="md", 
                    style={
                        "float": "right", 
                        "width": "38px", 
                        "height": "38px", 
                        "padding": "0", 
                        "fontSize": "1.4rem"
                    }
                ),
            ], width=3),
        ], className="g-0 mb-2"),
        dcc.Store(id="add-legs-store"),
    ]
