"""
Dashboard page - Main overview of trading performance
"""
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

from utils.analytics import get_dashboard_metrics, get_equity_curve, get_daily_pnl
from utils.db_utils import get_trades_dataframe

dash.register_page(__name__, path="/", title="Dashboard - TradeCraft")

def create_metric_card(title: str, value: str, color: str = "primary") -> dbc.Card:
    """Create a metric card for the dashboard"""
    return dbc.Card([
        dbc.CardBody([
            html.H4(value, className=f"text-{color}"),
            html.P(title, className="card-text")
        ])
    ], className="text-center")

def create_equity_curve_chart(df: pd.DataFrame) -> dcc.Graph:
    """Create equity curve chart"""
    fig = go.Figure()
    
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['cumulative_pnl'],
            mode='lines',
            name='Equity Curve',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_layout(
            title="Equity Curve",
            xaxis_title="Date",
            yaxis_title="Cumulative P&L ($)",
            height=400,
            template="plotly_white"
        )
    
    return dcc.Graph(figure=fig)

def create_daily_pnl_chart(df: pd.DataFrame) -> dcc.Graph:
    """Create daily P&L bar chart"""
    fig = go.Figure()
    
    if not df.empty:
        colors = ['green' if x >= 0 else 'red' for x in df['daily_pnl']]
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['daily_pnl'],
            marker_color=colors,
            name='Daily P&L'
        ))
        
        fig.update_layout(
            title="Daily P&L",
            xaxis_title="Date",
            yaxis_title="P&L ($)",
            height=400,
            template="plotly_white"
        )
    
    return dcc.Graph(figure=fig)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Trading Dashboard", className="mb-4"),
            html.P("Overview of your trading performance", className="text-muted")
        ])
    ]),
    
    # Metrics Row
    dbc.Row([
        dbc.Col([
            html.Div(id="metrics-cards")
        ], width=12)
    ], className="mb-4"),
    
    # Charts Row
    dbc.Row([
        dbc.Col([
            html.Div(id="equity-curve-chart")
        ], width=8),
        dbc.Col([
            html.Div(id="daily-pnl-chart")
        ], width=4)
    ], className="mb-4"),
    
    # Recent Trades
    dbc.Row([
        dbc.Col([
            html.H3("Recent Trades", className="mb-3"),
            html.Div(id="recent-trades-table")
        ])
    ])
], fluid=True)

@callback(
    [Output("metrics-cards", "children"),
     Output("equity-curve-chart", "children"),
     Output("daily-pnl-chart", "children"),
     Output("recent-trades-table", "children")],
    [Input("url", "pathname")]  # Will be added to app layout
)
def update_dashboard(pathname: str) -> tuple:
    """Update dashboard components"""
    try:
        # Get data
        trades_df = get_trades_dataframe()
        metrics = get_dashboard_metrics(trades_df)
        equity_df = get_equity_curve(trades_df)
        daily_df = get_daily_pnl(trades_df)
        
        # Create metric cards
        metric_cards = dbc.Row([
            dbc.Col([
                create_metric_card("Total P&L", f"${metrics['total_pnl']:,.2f}", 
                                 "success" if metrics['total_pnl'] >= 0 else "danger")
            ], width=3),
            dbc.Col([
                create_metric_card("Win Rate", f"{metrics['win_rate']:.1f}%")
            ], width=3),
            dbc.Col([
                create_metric_card("Total Trades", str(metrics['total_trades']))
            ], width=3),
            dbc.Col([
                create_metric_card("Avg Return", f"${metrics['avg_return']:,.2f}")
            ], width=3)
        ])
        
        # Create charts
        equity_chart = create_equity_curve_chart(equity_df)
        daily_chart = create_daily_pnl_chart(daily_df)
        
        # Recent trades table
        recent_trades = trades_df.head(10) if not trades_df.empty else pd.DataFrame()
        
        if not recent_trades.empty:
            trades_table = dbc.Table.from_dataframe(
                recent_trades[['symbol', 'status', 'created_at', 'total_pnl']].round(2),
                striped=True, bordered=True, hover=True, size="sm"
            )
        else:
            trades_table = html.P("No trades found.")
        
        return metric_cards, equity_chart, daily_chart, trades_table
        
    except Exception as e:
        # Error handling
        error_card = dbc.Alert(f"Error loading dashboard: {str(e)}", color="danger")
        return error_card, html.Div(), html.Div(), html.Div()
