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

# Register this as a Dash page
dash.register_page(__name__, path="/trade_log", name="Trade Log")

USERNAME = "alice"  # For now, single-user mode

def get_trades_df(symbol: str = "", tag: str = "", start: str = "", end: str = "") -> pd.DataFrame:
    """Fetch and filter trades for the user as a DataFrame, with analytics columns for summary table and icons for notes/tags."""
    trades = db_access.fetch_trades_for_user(USERNAME)
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
        opened_at = pd.to_datetime(row["opened_at"])
        closed_at = pd.to_datetime(exit_leg["executed_at"]) if exit_leg else None
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
        tags_icon = f"🏷️" if row.get("tags") else ""
        analytics_list.append({
            "date": opened_at.date().isoformat(),
            "symbol": row["asset_symbol"],
            "status": status,
            "quantity": analytics["total_bought"],
            "entry_price": entry_leg["price"] if entry_leg else None,
            "exit_price": exit_leg["price"] if exit_leg else None,
            "entry_total": entry_total,
            "exit_total": exit_total,
            "hold_time": str(hold_time) if hold_time is not None else ("Open" if analytics["status"] == "open" else None),
            "return_dollar": return_dollar,
            "return_pct": return_pct,
            "notes_icon": notes_icon,
            "tags_icon": tags_icon,
            "notes": row.get("notes", ""),
            "tags": row.get("tags", ""),
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
    html.H2("Trade Log"),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="symbol-filter", placeholder="Filter by symbol", type="text", debounce=True),
        ], width=3),
        dbc.Col([
            dbc.Input(id="tag-filter", placeholder="Filter by tag", type="text", debounce=True),
        ], width=3),
        dbc.Col([
            dcc.DatePickerRange(
                id="date-filter",
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                display_format="YYYY-MM-DD"
            ),
        ], width=4),
        dbc.Col([
            dbc.Button("Clear Filters", id="clear-filters", color="secondary", outline=True, className="me-2"),
        ], width=2),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Today", id="quickfilter-today", color="primary", outline=True, size="sm"),
                dbc.Button("Yesterday", id="quickfilter-yesterday", color="primary", outline=True, size="sm"),
                dbc.Button("This Week", id="quickfilter-thisweek", color="primary", outline=True, size="sm"),
                dbc.Button("Last Week", id="quickfilter-lastweek", color="primary", outline=True, size="sm"),
                dbc.Button("This Month", id="quickfilter-thismonth", color="primary", outline=True, size="sm"),
                dbc.Button("Last Month", id="quickfilter-lastmonth", color="primary", outline=True, size="sm"),
                dbc.Button("All Time", id="quickfilter-alltime", color="primary", outline=True, size="sm"),
            ], size="sm", className="mb-2"),
        ], width=12),
    ], className="mb-2"),
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
        data=get_trades_df().to_dict("records"),
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        row_selectable="single",
        selected_rows=[],
        tooltip_data=[
            {
                "notes_icon": row["notes"] if row["notes_icon"] else None,
                "tags_icon": row["tags"] if row["tags_icon"] else None
            } for row in get_trades_df().to_dict("records")
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
    ],
    prevent_initial_call=True
)
def update_table(symbol, tag, start, end, clear):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("clear-filters"):
        return get_trades_df().to_dict("records")
    return get_trades_df(symbol or "", tag or "", start or "", end or "").to_dict("records")

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
