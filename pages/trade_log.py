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
