"""
Trade Log page - View and manage all trades
"""
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

from utils.db_utils import get_trades_dataframe, add_trade, update_trade, delete_trade
from models import Trade, TradeLeg, AssetType, TradeAction

dash.register_page(__name__, path="/trades", title="Trade Log - TradeCraft")

def create_trade_form() -> dbc.Form:
    """Create form for adding/editing trades"""
    return dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Symbol"),
                dbc.Input(id="trade-symbol", type="text", placeholder="AAPL")
            ], width=6),
            dbc.Col([
                dbc.Label("Asset Type"),
                dcc.Dropdown(
                    id="trade-asset-type",
                    options=[
                        {"label": "Stock", "value": "stock"},
                        {"label": "Option", "value": "option"}
                    ],
                    value="option"
                )
            ], width=6)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Action"),
                dcc.Dropdown(
                    id="trade-action",
                    options=[
                        {"label": "Buy", "value": "buy"},
                        {"label": "Sell", "value": "sell"},
                        {"label": "Buy to Open", "value": "buy_to_open"},
                        {"label": "Sell to Close", "value": "sell_to_close"}
                    ],
                    value="buy_to_open"
                )
            ], width=6),
            dbc.Col([
                dbc.Label("Quantity"),
                dbc.Input(id="trade-quantity", type="number", value=1, min=1)
            ], width=6)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Price"),
                dbc.Input(id="trade-price", type="number", step=0.01, min=0)
            ], width=6),
            dbc.Col([
                dbc.Label("Fees"),
                dbc.Input(id="trade-fees", type="number", step=0.01, value=0)
            ], width=6)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Date & Time"),
                dbc.Input(id="trade-datetime", type="datetime-local", 
                         value=datetime.now().strftime("%Y-%m-%dT%H:%M"))
            ], width=6),
            dbc.Col([
                dbc.Label("Status"),
                dcc.Dropdown(
                    id="trade-status",
                    options=[
                        {"label": "Open", "value": "OPEN"},
                        {"label": "Win", "value": "WIN"},
                        {"label": "Loss", "value": "LOSS"}
                    ],
                    value="OPEN"
                )
            ], width=6)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Tags (comma-separated)"),
                dbc.Input(id="trade-tags", type="text", placeholder="strategy, scalp, SPY")
            ], width=12)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Journal Entry"),
                dbc.Textarea(id="trade-journal", placeholder="Trade notes and analysis...")
            ], width=12)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Add Trade", id="add-trade-btn", color="primary", className="me-2"),
                dbc.Button("Clear", id="clear-form-btn", color="secondary", outline=True)
            ])
        ])
    ])

layout = dbc.Container([
    dcc.Store(id="trades-store"),
    
    dbc.Row([
        dbc.Col([
            html.H1("Trade Log", className="mb-4"),
            html.P("Add, edit, and view your trading history", className="text-muted")
        ])
    ]),
    
    # Add Trade Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Add New Trade", className="mb-0")
                ]),
                dbc.CardBody([
                    create_trade_form()
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Filters Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filters", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Symbol Filter"),
                            dbc.Input(id="symbol-filter", type="text", placeholder="Filter by symbol...")
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Status Filter"),
                            dcc.Dropdown(
                                id="status-filter",
                                options=[
                                    {"label": "All", "value": "all"},
                                    {"label": "Open", "value": "OPEN"},
                                    {"label": "Win", "value": "WIN"},
                                    {"label": "Loss", "value": "LOSS"}
                                ],
                                value="all"
                            )
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Date From"),
                            dbc.Input(id="date-from", type="date")
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Date To"),
                            dbc.Input(id="date-to", type="date")
                        ], width=3)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Trades Table
    dbc.Row([
        dbc.Col([
            html.Div(id="trades-table-container")
        ])
    ])
], fluid=True)

@callback(
    Output("trades-store", "data"),
    [Input("symbol-filter", "value"),
     Input("status-filter", "value"),
     Input("date-from", "value"),
     Input("date-to", "value")]
)
def update_trades_data(symbol_filter: str, status_filter: str, 
                      date_from: str, date_to: str) -> Dict[str, Any]:
    """Update trades data based on filters"""
    try:
        df = get_trades_dataframe()
        
        # Apply filters
        if symbol_filter:
            df = df[df['symbol'].str.contains(symbol_filter, case=False, na=False)]
        
        if status_filter and status_filter != "all":
            df = df[df['status'] == status_filter]
        
        if date_from:
            df = df[df['created_at'] >= date_from]
        
        if date_to:
            df = df[df['created_at'] <= date_to]
        
        return df.to_dict('records')
    
    except Exception as e:
        return []

@callback(
    Output("trades-table-container", "children"),
    [Input("trades-store", "data")]
)
def update_trades_table(trades_data: List[Dict[str, Any]]) -> html.Div:
    """Update trades table display"""
    if not trades_data:
        return dbc.Alert("No trades found with current filters.", color="info")
    
    df = pd.DataFrame(trades_data)
    
    # Format the data for display
    display_columns = ['symbol', 'status', 'created_at', 'asset_type', 'total_pnl']
    if all(col in df.columns for col in display_columns):
        display_df = df[display_columns].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_df['total_pnl'] = display_df['total_pnl'].round(2)
        
        return dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[
                {"name": "Symbol", "id": "symbol"},
                {"name": "Status", "id": "status"},
                {"name": "Date", "id": "created_at"},
                {"name": "Type", "id": "asset_type"},
                {"name": "P&L ($)", "id": "total_pnl", "type": "numeric", "format": {"specifier": ",.2f"}}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{status} = WIN'},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                },
                {
                    'if': {'filter_query': '{status} = LOSS'},
                    'backgroundColor': '#f8d7da',
                    'color': 'black',
                }
            ],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=20
        )
    
    return dbc.Alert("Error displaying trades data.", color="danger")

@callback(
    [Output("trade-symbol", "value"),
     Output("trade-quantity", "value"),
     Output("trade-price", "value"),
     Output("trade-fees", "value"),
     Output("trade-tags", "value"),
     Output("trade-journal", "value")],
    [Input("clear-form-btn", "n_clicks")]
)
def clear_form(n_clicks):
    """Clear the trade form"""
    if n_clicks:
        return "", 1, None, 0, "", ""
    return dash.no_update
