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

# Register this as a Dash page
dash.register_page(__name__, path="/trade_log", name="Trade Log")

USERNAME = "alice"  # For now, single-user mode

def get_trades_df(symbol: str = "", tag: str = "", start: str = "", end: str = "") -> pd.DataFrame:
    """Fetch and filter trades for the user as a DataFrame, with closed date."""
    trades = db_access.fetch_trades_for_user(USERNAME)
    df = pd.DataFrame(trades)
    # Add closed_at column if missing (for legacy/sample data)
    if "closed_at" not in df.columns:
        df["closed_at"] = None
    # Compute closed_at for trades that are closed but missing the value
    if not df.empty:
        for idx, row in df.iterrows():
            if not row.get("closed_at"):
                # If trade is closed, set closed_at to latest leg's executed_at
                legs = db_access.fetch_legs_for_trade(row["id"])
                if legs:
                    total_bought = sum(l['quantity'] for l in legs if l['action'] in ("buy", "buy to open"))
                    total_sold = sum(l['quantity'] for l in legs if l['action'] in ("sell", "sell to close"))
                    if total_bought == total_sold:
                        df.at[idx, "closed_at"] = max(l['executed_at'] for l in legs)
    if symbol:
        df = df[df["asset_symbol"].str.contains(symbol, case=False, na=False)]
    if tag:
        df = df[df["tags"].str.contains(tag, case=False, na=False)]
    if start:
        df = df[df["opened_at"] >= start]
    if end:
        df = df[df["opened_at"] <= end]
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
            {"name": "ID", "id": "id"},
            {"name": "Symbol", "id": "asset_symbol"},
            {"name": "Type", "id": "asset_type"},
            {"name": "Opened", "id": "opened_at"},
            {"name": "Closed", "id": "closed_at"},
            {"name": "Tags", "id": "tags"},
            {"name": "Notes", "id": "notes"},
        ],
        data=get_trades_df().to_dict("records"),
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        row_selectable="single",
        selected_rows=[],
    ),
    # Add a hidden Location component for programmatic navigation (no style arg)
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
