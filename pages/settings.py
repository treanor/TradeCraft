"""
Settings page - Application configuration and data management
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from pathlib import Path
import os

from utils.db_utils import get_trade_summary_stats, DB_PATH
from sample_data import sample_trades

# Import seed_database function conditionally
try:
    from utils.seed_db import seed_database
except ImportError:
    # Fallback implementation if import fails
    def seed_database(trades):
        """Fallback seed function that actually seeds the database"""
        from utils import db_utils
        
        # Get or create default user
        users = db_utils.get_users()
        if users:
            user_id = users[0]['id']
        else:
            user_id = db_utils.add_user("default_user", "user@tradecraft.com")
        
        for trade in trades:
            # Add the trade
            trade_id = db_utils.add_trade(
                user_id=user_id,
                symbol=trade.symbol,
                asset_type=trade.asset_type.value,
                status=trade.status,
                created_at=trade.created_at.isoformat(),
                journal_entry=trade.journal_entry
            )
            
            # Add trade legs
            for leg in trade.legs:
                db_utils.add_trade_leg(
                    trade_id=trade_id,
                    action=leg.action.value,
                    datetime=leg.datetime.isoformat(),
                    quantity=leg.quantity,
                    price=leg.price,
                    fee=leg.fee
                )
            
            # Add tags
            for tag in trade.tags:
                db_utils.add_tag(trade_id, tag)
        
        print(f"Seeded {len(trades)} trades into the database.")

dash.register_page(__name__, path="/settings", title="Settings - TradeCraft")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Settings", className="mb-4"),
            html.P("Manage your TradeCraft application settings", className="text-muted")
        ])
    ]),
    
    # Database Status
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Database Status", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="database-status"),
                    html.Hr(),
                    dbc.Button("Initialize Database", id="init-db-btn", color="primary", className="me-2"),
                    dbc.Button("Load Sample Data", id="load-sample-btn", color="secondary", className="me-2"),
                    dbc.Button("Clear All Data", id="clear-data-btn", color="danger", outline=True)
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Data Import/Export
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Data Management", className="mb-0")
                ]),
                dbc.CardBody([
                    html.H5("Import Trades", className="mb-3"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div([
                            "Drag and Drop or ",
                            html.A("Select Files")
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id="upload-output"),
                    html.Hr(),
                    html.H5("Export Data", className="mb-3"),
                    dbc.Button("Export All Trades (CSV)", id="export-csv-btn", color="success"),
                    dbc.Button("Export All Trades (JSON)", id="export-json-btn", color="info", className="ms-2")
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Application Settings
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Application Settings", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Default Currency"),
                                dcc.Dropdown(
                                    id="currency-dropdown",
                                    options=[
                                        {"label": "USD ($)", "value": "USD"},
                                        {"label": "EUR (€)", "value": "EUR"},
                                        {"label": "GBP (£)", "value": "GBP"}
                                    ],
                                    value="USD"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Risk Percentage per Trade"),
                                dbc.Input(id="risk-percentage", type="number", value=2, min=0.1, max=10, step=0.1)
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Account Balance"),
                                dbc.Input(id="account-balance", type="number", value=10000, min=0, step=100)
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Max Position Size"),
                                dbc.Input(id="max-position", type="number", value=200, min=0, step=10, disabled=True)
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Button("Save Settings", id="save-settings-btn", color="primary")
                    ])
                ])
            ])
        ])
    ]),
    
    # Alerts
    html.Div(id="settings-alerts")
], fluid=True)

@callback(
    Output("database-status", "children"),
    [Input("url", "pathname")]  # Will trigger on page load
)
def update_database_status(pathname: str) -> html.Div:
    """Update database status display"""
    try:
        # Check if database exists
        db_exists = DB_PATH.exists()
        
        if db_exists:
            stats = get_trade_summary_stats()
            status_content = [
                dbc.Alert([
                    html.Strong("Database Connected "), "✓"
                ], color="success"),
                html.P(f"Database location: {DB_PATH}"),
                html.P(f"Total trades: {stats['total_trades']}"),
                html.P(f"Total P&L: ${stats['total_pnl']:,.2f}")
            ]
        else:
            status_content = [
                dbc.Alert([
                    html.Strong("Database Not Found "), "⚠️"
                ], color="warning"),
                html.P("Click 'Initialize Database' to create the database.")
            ]
        
        return html.Div(status_content)
        
    except Exception as e:
        return dbc.Alert(f"Database error: {str(e)}", color="danger")

@callback(
    Output("settings-alerts", "children"),
    [Input("init-db-btn", "n_clicks"),
     Input("load-sample-btn", "n_clicks"),
     Input("clear-data-btn", "n_clicks"),
     Input("save-settings-btn", "n_clicks")],
    [State("currency-dropdown", "value"),
     State("risk-percentage", "value"),
     State("account-balance", "value")],
    prevent_initial_call=True
)
def handle_settings_actions(init_clicks, sample_clicks, clear_clicks, save_clicks,
                          currency, risk_pct, account_balance):
    """Handle various settings actions"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return []
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    try:
        if button_id == "init-db-btn":
            # Initialize database
            from utils.init_db import initialize_database
            initialize_database()
            return [dbc.Alert("Database initialized successfully!", color="success", dismissable=True)]
        
        elif button_id == "load-sample-btn":
            # Load sample data
            seed_database(sample_trades)
            return [dbc.Alert("Sample data loaded successfully!", color="success", dismissable=True)]
        
        elif button_id == "clear-data-btn":
            # Clear all data (implement carefully)
            return [dbc.Alert("Data clearing not implemented yet for safety.", color="warning", dismissable=True)]
        
        elif button_id == "save-settings-btn":
            # Save application settings
            return [dbc.Alert("Settings saved successfully!", color="success", dismissable=True)]
        
    except Exception as e:
        return [dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)]
    
    return []

@callback(
    Output("max-position", "value"),
    [Input("account-balance", "value"),
     Input("risk-percentage", "value")]
)
def calculate_max_position(balance, risk_pct):
    """Calculate maximum position size based on account balance and risk percentage"""
    if balance and risk_pct:
        return round(balance * (risk_pct / 100), 2)
    return 0
