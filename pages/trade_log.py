"""
Trade Log Page for Trade Craft
- Displays a table of trades for the user
- Supports filtering by symbol, date, and tags
"""
import dash
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils import db_access
import pandas as pd
from dash.dependencies import ALL
from dash import ctx
from datetime import date, timedelta, datetime
from components.filters import filter_header, user_account_dropdowns  # Import the reusable filter_header and user_account_dropdowns components

# Register this as a Dash page
dash.register_page(__name__, path="/trade_log", name="Trade Log")

USERNAME = "alice"  # For now, single-user mode

def get_trades_df(user_id: int, account_id: int, symbol: str = "", tag: str = "", start: str = "", end: str = "") -> pd.DataFrame:
    """Fetch and filter trades for the user/account as a DataFrame, with analytics columns for summary table and icons for notes/tags."""
    trades = db_access.fetch_trades_for_user_and_account(user_id, account_id)
    df = pd.DataFrame(trades)
    if df.empty:
        return df
    # Add analytics columns for each trade
    analytics_list = []
    for _, row in df.iterrows():
        analytics = db_access.trade_analytics(row["id"])
        entry_leg = None
        exit_leg = None
        legs = db_access.fetch_legs_for_trade(row["id"])
        if legs:
            entry_leg = min(legs, key=lambda l: l["executed_at"])
            # Only set exit_leg if trade is closed
            if analytics["status"] == "closed":
                exit_leg = max([l for l in legs if l["action"] in ("sell", "sell to close")], key=lambda l: l["executed_at"], default=None)
        # Hold time
        opened_at = pd.to_datetime(row["opened_at"], utc=True, errors="coerce")
        closed_at = pd.to_datetime(exit_leg["executed_at"], utc=True, errors="coerce") if exit_leg else None
        hold_time = (closed_at - opened_at) if closed_at is not None else None
        # Return $ and %
        entry_total = entry_leg["quantity"] * entry_leg["price"] if entry_leg else None
        exit_total = exit_leg["quantity"] * exit_leg["price"] if exit_leg else None
        return_dollar = analytics["realized_pnl"] if analytics["status"] == "closed" else None
        return_pct = (return_dollar / entry_total * 100) if (return_dollar is not None and entry_total) else None
        # Win/loss/open status
        if analytics["status"] == "open":
            status = "Open"
        elif return_dollar is not None:
            status = "Win" if return_dollar > 0 else ("Loss" if return_dollar < 0 else "Even")
        else:
            status = "-"
        # Add icon columns for notes/tags
        notes_icon = f"📝" if row.get("notes") else ""
        # --- Use normalized tags ---
        tags_list = db_access.get_tags_for_trade(row["id"])
        tags_str = ", ".join(tags_list)
        tags_icon = f"🏷️" if tags_list else ""
        # --- Use normalized symbols ---
        symbols_list = db_access.get_symbols_for_trade(row["id"])
        symbols_str = ", ".join(symbols_list)
        analytics_list.append({
            "date": opened_at.date().isoformat(),
            "symbol": symbols_str,
            "status": status,
            "quantity": analytics["total_bought"],
            "entry_price": entry_leg["price"] if entry_leg else None,
            "exit_price": exit_leg["price"] if exit_leg else None,
            "hold_time": str(hold_time) if hold_time is not None else ("Open" if analytics["status"] == "open" else None),
            "return_dollar": return_dollar,
            "return_pct": return_pct,
            "notes_icon": notes_icon,
            "tags_icon": tags_icon,
            "notes": row.get("notes", ""),
            "tags": tags_str,
            "id": row["id"]
        })
    df = pd.DataFrame(analytics_list)
    # Filtering
    if symbol:
        df = df[df["symbol"].str.contains(symbol, case=False, na=False)]
    if tag:
        df = df[df["tags"].str.contains(tag, case=False, na=False)]
    if start:
        df = df[df["date"] >= start]
    if end:
        df = df[df["date"] <= end]
    return df

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Trade Craft", className="text-light"), width="auto"),
        dbc.Col(user_account_dropdowns(), width="auto", style={"marginLeft": "auto"}),
    ], className="align-items-center mb-4 g-0"),
    html.Div(filter_header(prefix="", show_add_trade=True), className="mb-2"),  # Use the reusable filter_header component
    # Remove any dbc.Row or code that creates a second set of quick filter buttons (Today, Yesterday, This Week, etc.) from the Trade Log layout. Only the filter_header should provide these buttons now.
    # Add modal for manual trade entry (cleaned up, no target/stop-loss, improved spacing, date picker for legs)
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add New Trade")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
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
                        dbc.Input(id="add-symbol", type="text", required=True, style={"width": "100%", "fontSize": "1.05rem"}),
                    ], width=2, style={"maxWidth": "160px", "flex": "0 0 160px", "paddingRight": "32px"}),
                    dbc.Col([
                        dbc.Label("Journal/Notes", className="mb-1"),
                        dbc.Textarea(id="add-notes", placeholder="Optional notes...", style={"width": "100%", "height": 38, "fontSize": "1.05rem"}),
                    ], width=8, style={"minWidth": "320px", "flex": "1 1 320px"}),
                ], className="mb-3 g-3 align-items-end flex-nowrap", style={"flexWrap": "nowrap", "display": "flex"}),
                html.Hr(className="my-3"),
                html.H5("Legs", className="mb-3 mt-3"),
                html.Div(
                    id="add-legs-table",
                    style={
                        "background": "#fff",  # Use plain white for a clean look
                        "border": "1px solid #e2e3e5",
                        "borderRadius": "12px",
                        "padding": "18px 18px 10px 18px",
                        "marginBottom": "18px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",  # subtle shadow for separation
                    }
                ),
                dbc.Row([
                    dbc.Col([], width=9),
                    dbc.Col([
                        dbc.Button("+", id="add-leg-btn", color="primary", outline=True, className="my-2", size="md", style={"float": "right", "width": "38px", "height": "38px", "padding": "0", "fontSize": "1.4rem"}),
                    ], width=3),
                ], className="g-0 mb-2"),
                dcc.Store(id="add-legs-store"),
            ]),
        ], style={"paddingTop": "18px", "paddingBottom": "0"}),
        dbc.ModalFooter([
            dbc.Button("Save", id="add-trade-submit", color="success", className="me-2", style={"fontSize": "1.1rem", "padding": "8px 24px"}),
            dbc.Button("Cancel", id="add-trade-cancel", color="secondary", style={"fontSize": "1.1rem", "padding": "8px 24px"}),
        ]),
    ], id="add-trade-modal", is_open=False, size="xl", style={"minWidth": "900px", "maxWidth": "1200px"}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="equity-curve-chart", config={"displayModeBar": False}),
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Summary Stats"),
                dbc.CardBody([
                    html.Div(id="trade-log-summary-stats")
                ]),
            ]),
        ], width=4),
    ], className="mb-4"),
    dash_table.DataTable(
        id="trade-table",
        columns=[
            {"name": "Date", "id": "date"},
            {"name": "Symbol", "id": "symbol"},
            {"name": "Status", "id": "status"},
            {"name": "Quantity", "id": "quantity"},
            {"name": "Entry Price", "id": "entry_price", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Exit Price", "id": "exit_price", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Entry Total", "id": "entry_total", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Exit Total", "id": "exit_total", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Hold Time", "id": "hold_time"},
            {"name": "Return $", "id": "return_dollar", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Return %", "id": "return_pct", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Notes", "id": "notes_icon", "presentation": "markdown"},
            {"name": "Tags", "id": "tags_icon", "presentation": "markdown"},
        ],
        data=get_trades_df(0, 0).to_dict("records"),
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        row_selectable="single",
        selected_rows=[],
        tooltip_data=[
            {
                "notes_icon": row["notes"] if row["notes_icon"] else None,
                "tags_icon": row["tags"] if row["tags_icon"] else None
            } for row in get_trades_df(0, 0).to_dict("records")
        ],
        tooltip_duration=None,
        # Remove clickability: icons are just static markdown, not links
        markdown_options={"link_target": None},
    ),
    dcc.Location(id="trade-log-navigate", refresh=True),
], fluid=True)

@callback(
    Output("trade-table", "data"),
    [
        Input("symbol-filter", "value"),
        Input("tag-filter", "value"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("clear-filters", "n_clicks"),
        Input("user-store", "data"),
        Input("account-dropdown", "value"),
    ],
    prevent_initial_call=True
)
def update_table(symbol, tag, start, end, clear, user_id, account_id):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("clear-filters"):
        return get_trades_df(user_id, account_id).to_dict("records")
    return get_trades_df(user_id, account_id, symbol or "", tag or "", start or "", end or "").to_dict("records")

@callback(
    Output("date-filter", "start_date"),
    Output("date-filter", "end_date"),
    [
        Input("quickfilter-today", "n_clicks"),
        Input("quickfilter-yesterday", "n_clicks"),
        Input("quickfilter-thisweek", "n_clicks"),
        Input("quickfilter-lastweek", "n_clicks"),
        Input("quickfilter-thismonth", "n_clicks"),
        Input("quickfilter-lastmonth", "n_clicks"),
        Input("quickfilter-alltime", "n_clicks"),
    ],
    prevent_initial_call=True
)
def set_quick_date_filter(
    today, yesterday, thisweek, lastweek, thismonth, lastmonth, alltime
):
    triggered = ctx.triggered_id
    today_dt = date.today()
    if triggered == "quickfilter-today":
        return today_dt.isoformat(), today_dt.isoformat()
    elif triggered == "quickfilter-yesterday":
        yest = today_dt - timedelta(days=1)
        return yest.isoformat(), yest.isoformat()
    elif triggered == "quickfilter-thisweek":
        start = today_dt - timedelta(days=today_dt.weekday())
        return start.isoformat(), today_dt.isoformat()
    elif triggered == "quickfilter-lastweek":
        start = today_dt - timedelta(days=today_dt.weekday() + 7)
        end = start + timedelta(days=6)
        return start.isoformat(), end.isoformat()
    elif triggered == "quickfilter-thismonth":
        start = today_dt.replace(day=1)
        return start.isoformat(), today_dt.isoformat()
    elif triggered == "quickfilter-lastmonth":
        first_this_month = today_dt.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = last_month_end
        return start.isoformat(), end.isoformat()
    elif triggered == "quickfilter-alltime":
        return None, None
    return dash.no_update, dash.no_update

# Navigation callback: when a row is selected, navigate to detail page
@callback(
    Output("trade-log-navigate", "href"),
    Input("trade-table", "selected_rows"),
    State("trade-table", "data"),
    prevent_initial_call=True
)
def go_to_trade_detail(selected_rows, data):
    if selected_rows:
        trade_id = data[selected_rows[0]]["id"]
        return f"/trade_detail/{trade_id}"
    return dash.no_update

@callback(
    [Output("equity-curve-chart", "figure"), Output("trade-log-summary-stats", "children")],
    [
        Input("trade-table", "data"),
        State("date-filter", "start_date"),
        State("date-filter", "end_date"),
    ],
)
def update_equity_and_stats(table_data: list[dict], start_date: str, end_date: str) -> tuple:
    """Update the equity curve chart and summary stats based on filtered trades.
    For 'today' and 'yesterday', group by hour; otherwise, group by day.
    """
    import plotly.graph_objs as go
    import pandas as pd
    if not table_data or len(table_data) == 0:
        fig = go.Figure()
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), template="plotly_white")
        stats = [html.Div("No trades to summarize.")]
        return fig, stats
    df = pd.DataFrame(table_data)
    df = df.sort_values("date")
    # Determine grouping granularity
    group_by = "date"  # default: group by day
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            if (end - start).days <= 1:
                # For today or yesterday, group by hour
                group_by = "hour"
        except Exception:
            group_by = "date"
    # Equity curve logic
    if group_by == "hour":
        # If possible, use a datetime column for hour grouping
        if "opened_at" in df.columns:
            df["opened_at_dt"] = pd.to_datetime(df["opened_at"], errors="coerce")
        else:
            # Fallback: try to get from index or skip
            df["opened_at_dt"] = pd.to_datetime(df["date"], errors="coerce")
        df["hour"] = df["opened_at_dt"].dt.strftime("%Y-%m-%d %H:00")
        df_grouped = df.groupby("hour", as_index=False)["return_dollar"].sum()
        df_grouped = df_grouped.sort_values("hour")
        df_grouped["cum_pnl"] = df_grouped["return_dollar"].fillna(0).cumsum()
        x = df_grouped["hour"]
        y = df_grouped["cum_pnl"]
    else:
        # Group by date, sum return_dollar per day
        df_grouped = df.groupby("date", as_index=False)["return_dollar"].sum()
        df_grouped = df_grouped.sort_values("date")
        df_grouped["cum_pnl"] = df_grouped["return_dollar"].fillna(0).cumsum()
        x = df_grouped["date"]
        y = df_grouped["cum_pnl"]
    fig = go.Figure(go.Scatter(x=x, y=y, mode="lines+markers", name="Equity Curve"))
    fig.update_layout(
        title="Equity Curve",
        xaxis_title="Date/Hour" if group_by == "hour" else "Date",
        yaxis_title="Cumulative P&L ($)",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        template="plotly_white"
    )
    # Stats (unchanged)
    wins = df[(df["status"] == "Win") & df["return_dollar"].notnull()]
    losses = df[(df["status"] == "Loss") & df["return_dollar"].notnull()]
    open_trades = df[df["status"] == "Open"]
    avg_win = wins["return_dollar"].mean() if not wins.empty else 0.0
    avg_loss = losses["return_dollar"].mean() if not losses.empty else 0.0
    total_pnl = df["return_dollar"].sum(skipna=True)
    stats = dbc.ListGroup([
        dbc.ListGroupItem([html.B("Wins: "), f"{len(wins)}"]),
        dbc.ListGroupItem([html.B("Losses: "), f"{len(losses)}"]),
        dbc.ListGroupItem([html.B("Open: "), f"{len(open_trades)}"]),
        dbc.ListGroupItem([html.B("Avg Win: "), f"${avg_win:.2f}"]),
        dbc.ListGroupItem([html.B("Avg Loss: "), f"${avg_loss:.2f}"]),
        dbc.ListGroupItem([html.B("Total P&L: "), f"${total_pnl:.2f}"]),
    ])
    return fig, stats

@callback(
    Output("add-trade-modal", "is_open"),
    [Input("add-trade-btn", "n_clicks"), Input("add-trade-cancel", "n_clicks"), Input("add-trade-submit", "n_clicks")],
    [State("add-trade-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_add_trade_modal(
    btn_click: int, cancel_click: int, submit_click: int, is_open: bool
) -> bool:
    """Open modal on Add Trade button, close on Cancel or Submit."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger == "add-trade-btn":
        return True
    if trigger in ("add-trade-cancel", "add-trade-submit"):
        return False
    return is_open

def get_user_id(username: str) -> int:
    """Fetch user_id from username."""
    with db_access.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"User not found: {username}")
        return row[0]

def get_asset_type(symbol: str) -> str:
    """Guess asset type from symbol (very basic, extend as needed)."""
    if symbol.endswith('USD'):
        if symbol.startswith('BTC') or symbol.startswith('ETH'):
            return 'crypto'
        return 'forex'
    if symbol.endswith('C') or symbol.endswith('P'):
        return 'option'
    if symbol.isalpha() and len(symbol) <= 5:
        return 'stock'
    if symbol.isupper() and len(symbol) > 5:
        return 'future'
    return 'other'

@callback(
    [
        Output("trade-table", "data", allow_duplicate=True),
        Output("add-trade-modal", "is_open", allow_duplicate=True),
        Output("add-legs-store", "data", allow_duplicate=True),
    ],
    [Input("add-trade-submit", "n_clicks")],
    [
        State("add-market", "value"),
        State("add-symbol", "value"),
        State("add-notes", "value"),  # Removed target and stoploss
        State("add-legs-store", "data"),
    ],
    prevent_initial_call=True
)
def add_trade_submit(
    n_clicks: int,
    market: str,
    symbol: str,
    notes: str,
    legs: list,
):
    """Handle Add Trade form submission: insert new trade with all legs and update table."""
    if not n_clicks or not symbol or not legs or len(legs) == 0:
        raise dash.exceptions.PreventUpdate
    user_id = get_user_id(USERNAME)
    asset_type = market or get_asset_type(symbol)
    # Use first leg's date and time as opened_at
    first_leg = legs[0]
    opened_at = f"{first_leg.get('date', '')}T{first_leg.get('time', '')}" if first_leg.get('date') and first_leg.get('time') else datetime.now().isoformat()
    trade_id = db_access.insert_trade(
        user_id,
        symbol,
        asset_type,
        opened_at,
        notes or "",
        "",
    )
    for leg in legs:
        executed_at = f"{leg.get('date', '')}T{leg.get('time', '')}" if leg.get('date') and leg.get('time') else datetime.now().isoformat()
        db_access.insert_trade_leg(
            trade_id=trade_id,
            action=leg["action"],
            quantity=leg["quantity"],
            price=leg["price"],
            fees=leg["fee"],
            executed_at=executed_at,
            notes="",
        )
    new_data = get_trades_df().to_dict("records")
    return new_data, False, []

@callback(
    Output("add-legs-table", "children"),
    [Input("add-legs-store", "data")],
    prevent_initial_call=True
)
def render_legs_table(legs: list | None):
    """Render the legs table from the store."""
    if not legs:
        return html.Div("No legs. Add at least one leg.")
    rows = []
    for i, leg in enumerate(legs):
        rows.append(
            dbc.Row([
                dbc.Col([
                    dbc.Button("✖", id={"type": "remove-leg-btn", "index": i}, color="danger", size="md", className="me-2", style={"padding": "0 10px", "fontSize": "1.3rem", "height": "38px", "width": "38px"}),
                    dbc.Select(
                        id={"type": "leg-action", "index": i},
                        options=[{"label": "BUY", "value": "buy"}, {"label": "SELL", "value": "sell"}],
                        value=leg.get("action", "buy"),
                        size="md",
                        style={"width": "90px", "fontSize": "1rem", "display": "inline-block", "marginLeft": "8px"}
                    ),
                ], width=2, style={"maxWidth": "140px", "flex": "0 0 140px", "paddingRight": "12px", "display": "flex", "alignItems": "center"}),
                dbc.Col([
                    dcc.DatePickerSingle(
                        id={"type": "leg-date", "index": i},
                        date=leg.get("date"),
                        display_format="YYYY-MM-DD",
                        style={"width": "100%", "fontSize": "1rem"}
                    ),
                ], width=2, style={"maxWidth": "140px", "flex": "0 0 140px", "paddingRight": "12px"}),
                dbc.Col([
                    dbc.Input(
                        id={"type": "leg-time", "index": i},
                        type="time",
                        value=leg.get("time", "09:30"),
                        size="md",
                        style={"width": "100%", "fontSize": "1rem"}
                    ),
                ], width=2, style={"maxWidth": "120px", "flex": "0 0 120px", "paddingRight": "12px"}),
                dbc.Col([
                    dbc.Input(
                        id={"type": "leg-quantity", "index": i},
                        type="number",
                        value=leg.get("quantity", 1),
                        min=1,
                        size="md",
                        style={"width": "100%", "fontSize": "1rem"}
                    ),
                ], width=2, style={"maxWidth": "120px", "flex": "0 0 120px", "paddingRight": "12px"}),
                dbc.Col([
                    dbc.Input(
                        id={"type": "leg-price", "index": i},
                        type="number",
                        value=leg.get("price", 1.0),
                        min=0,
                        step=0.01,
                        size="md",
                        style={"width": "100%", "fontSize": "1rem"}
                    ),
                ], width=2, style={"maxWidth": "120px", "flex": "0 0 120px", "paddingRight": "12px"}),
                dbc.Col([
                    dbc.Input(
                        id={"type": "leg-fee", "index": i},
                        type="number",
                        value=leg.get("fee", 0.0),
                        min=0,
                        step=0.01,
                        size="md",
                        style={"width": "100%", "fontSize": "1rem"}
                    ),
                ], width=2, style={"maxWidth": "120px", "flex": "0 0 120px"}),
            ], className="mb-2 g-2 align-items-center flex-nowrap", style={"flexWrap": "nowrap", "display": "flex", "marginBottom": "8px"})
        )
    return html.Div([
        dbc.Row([
            dbc.Col("Action", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "140px", "flex": "0 0 140px"}),
            dbc.Col("Date", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "140px", "flex": "0 0 140px"}),
            dbc.Col("Time", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "120px", "flex": "0 0 120px"}),
            dbc.Col("Quantity", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "120px", "flex": "0 0 120px"}),
            dbc.Col("Price", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "120px", "flex": "0 0 120px"}),
            dbc.Col("Fee", width=2, style={"fontWeight": "bold", "fontSize": "1.05rem", "maxWidth": "120px", "flex": "0 0 120px"}),
        ], className="mb-2 g-2 flex-nowrap", style={"flexWrap": "nowrap", "display": "flex", "marginBottom": "10px"}),
        *rows
    ])

@callback(
    Output("add-legs-store", "data", allow_duplicate=True),
    [
        Input({"type": "remove-leg-btn", "index": ALL}, "n_clicks")
    ],
    [State("add-legs-store", "data")],
    prevent_initial_call=True
)
def remove_leg(remove_clicks, legs):
    """Remove a leg row when its remove button is clicked."""
    ctx = dash.callback_context
    if not ctx.triggered or not legs:
        raise dash.exceptions.PreventUpdate
    for i, btn in enumerate(remove_clicks):
        if btn:
            legs.pop(i)
            break
    return legs

@callback(
    Output("add-legs-store", "data", allow_duplicate=True),
    [
        Input({"type": "leg-action", "index": ALL}, "value"),
        Input({"type": "leg-date", "index": ALL}, "date"),
        Input({"type": "leg-time", "index": ALL}, "value"),
        Input({"type": "leg-quantity", "index": ALL}, "value"),
        Input({"type": "leg-price", "index": ALL}, "value"),
        Input({"type": "leg-fee", "index": ALL}, "value"),
    ],
    [State("add-legs-store", "data")],
    prevent_initial_call=True
)
def update_leg_fields(actions, dates, times, quantities, prices, fees, legs):
    """Update the legs store when any field in any leg row changes."""
    if not legs:
        raise dash.exceptions.PreventUpdate
    for i in range(len(legs)):
        legs[i]["action"] = actions[i]
        legs[i]["date"] = dates[i]
        legs[i]["time"] = times[i]
        legs[i]["quantity"] = quantities[i]
        legs[i]["price"] = prices[i]
        legs[i]["fee"] = fees[i]
    return legs

@callback(
    Output("add-legs-store", "data"),
    [Input("add-leg-btn", "n_clicks")],
    [State("add-legs-store", "data")],
    prevent_initial_call=True
)
def add_leg(n_clicks: int, legs: list | None) -> list:
    """Add a new leg row to the legs store."""
    if legs is None:
        legs = []
    from datetime import datetime
    now = datetime.now()
    legs.append({
        "action": "buy",
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "quantity": 1,
        "price": 1.0,
        "fee": 0.0,
    })
    return legs

@callback(
    Output("symbol-filter", "value", allow_duplicate=True),
    Output("tag-filter", "value", allow_duplicate=True),
    Output("date-filter", "start_date", allow_duplicate=True),
    Output("date-filter", "end_date", allow_duplicate=True),
    Input("clear-filters", "n_clicks"),
    prevent_initial_call=True
)
def clear_trade_log_filters(n_clicks):
    return None, None, None, None
