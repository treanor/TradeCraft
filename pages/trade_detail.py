"""
Trade Detail Page for Trade Craft
- Shows trade legs and analytics for a selected trade
"""
import dash
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils import db_access
import pandas as pd

# Register this as a Dash page
# URL: /trade_detail/<trade_id>
dash.register_page(__name__, path_template="/trade_detail/<trade_id>", name="Trade Detail")

USERNAME = "alice"  # For now, single-user mode

def get_trade_detail(trade_id: int):
    # Fetch trade, legs, and analytics
    trades = db_access.fetch_trades_for_user(USERNAME)
    trade = next((t for t in trades if t["id"] == trade_id), None)
    if not trade:
        return None, None, None
    legs = db_access.fetch_legs_for_trade(trade_id)
    analytics = db_access.trade_analytics(trade_id)
    return trade, legs, analytics

layout = dbc.Container([
    html.H2("Trade Detail"),
    dcc.Location(id="trade-detail-url"),
    html.Div(id="trade-detail-content"),
], fluid=True)

@callback(
    Output("trade-detail-content", "children"),
    Input("trade-detail-url", "pathname"),
)
def render_trade_detail(pathname):
    # Extract trade_id from URL
    import re
    m = re.match(r"/trade_detail/(\d+)", pathname or "")
    if not m:
        return dbc.Alert("Invalid trade ID in URL.", color="danger")
    trade_id = int(m.group(1))
    trade, legs, analytics = get_trade_detail(trade_id)
    if not trade:
        return dbc.Alert("Trade not found.", color="warning")
    # Trade summary
    summary = dbc.Card([
        dbc.CardHeader(f"{trade['asset_symbol']} ({trade['asset_type']})"),
        dbc.CardBody([
            html.P(f"Opened: {trade['opened_at']}", className="mb-1"),
            html.P(f"Closed: {trade.get('closed_at', '-')}", className="mb-1"),
            html.P(f"Tags: {trade.get('tags', '-')}", className="mb-1"),
            html.P(f"Notes: {trade.get('notes', '-')}", className="mb-1"),
        ]),
    ], className="mb-3")
    # Analytics
    analytics_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Total Bought"), html.Th("Total Sold"), html.Th("Avg Buy Price"), html.Th("Avg Sell Price"),
            html.Th("Total Fees"), html.Th("Realized P&L"), html.Th("Open Qty"), html.Th("Status")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(analytics["total_bought"]),
                html.Td(analytics["total_sold"]),
                html.Td(f"{analytics['avg_buy_price']:.2f}"),
                html.Td(f"{analytics['avg_sell_price']:.2f}"),
                html.Td(f"{analytics['total_fees']:.2f}"),
                html.Td(f"{analytics['realized_pnl']:.2f}"),
                html.Td(analytics["open_qty"]),
                html.Td(analytics["status"].capitalize()),
            ])
        ])
    ], bordered=True, striped=True, hover=True, className="mb-3")
    # Legs table
    legs_df = pd.DataFrame(legs)
    legs_table = dash_table.DataTable(
        columns=[
            {"name": "Action", "id": "action"},
            {"name": "Quantity", "id": "quantity"},
            {"name": "Price", "id": "price"},
            {"name": "Fees", "id": "fees"},
            {"name": "Executed At", "id": "executed_at"},
            {"name": "Notes", "id": "notes"},
        ],
        data=legs_df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        page_size=20,
    )
    return [
        dbc.Button("Back to Trade Log", href="/trade_log", color="secondary", className="mb-3"),
        summary,
        html.H5("Trade Analytics"),
        analytics_table,
        html.H5("Trade Legs"),
        legs_table,
    ]
