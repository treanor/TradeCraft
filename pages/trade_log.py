"""
Trade Log page for TradeCraft.
Displays a table of all trades for the sample user.
"""
import dash
from dash import html
from dash import dash_table
from utils import db_utils

# Fetch trades for sample user (user_id=1)
trades = db_utils.get_trades(1)

# Define columns for display
columns = [
    {"name": "Symbol", "id": "symbol"},
    {"name": "Asset Type", "id": "asset_type"},
    {"name": "Status", "id": "status"},
    {"name": "Created At", "id": "created_at"},
    {"name": "Journal Entry", "id": "journal_entry"},
]

layout = html.Div([
    html.H2("Trade Log"),
    dash_table.DataTable(
        id="trade-log-table",
        columns=columns,
        data=trades,
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        style_header={"fontWeight": "bold"},
    )
])

# Dash Pages discovery: set required module variables for Dash Pages
path = "/trade-log"
name = "Trade Log"
description = "View all trades in your journal."
