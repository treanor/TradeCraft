"""
Analytics page - Advanced trading analytics and charts
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

from utils.analytics import (
    get_symbol_performance, 
    get_monthly_performance,
    get_win_loss_distribution,
    get_trade_duration_analysis,
    get_drawdown_analysis
)
from utils.db_utils import get_trades_dataframe

dash.register_page(__name__, path="/analytics", title="Analytics - TradeCraft")

def create_performance_chart(df: pd.DataFrame, title: str) -> dcc.Graph:
    """Create a performance chart"""
    fig = go.Figure()
    
    if not df.empty and 'total_pnl' in df.columns:
        colors = ['green' if x >= 0 else 'red' for x in df['total_pnl']]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['total_pnl'],
            marker_color=colors,
            name='P&L'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="P&L ($)",
            height=400,
            template="plotly_white"
        )
    
    return dcc.Graph(figure=fig)

def create_win_loss_pie(win_rate: float, loss_rate: float) -> dcc.Graph:
    """Create win/loss pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=['Wins', 'Losses'],
        values=[win_rate, loss_rate],
        marker_colors=['green', 'red']
    )])
    
    fig.update_layout(
        title="Win/Loss Distribution",
        height=400,
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig)

def create_drawdown_chart(df: pd.DataFrame) -> dcc.Graph:
    """Create drawdown chart"""
    fig = go.Figure()
    
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['drawdown'],
            fill='tonexty',
            name='Drawdown',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="Equity Drawdown",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            height=400,
            template="plotly_white"
        )
    
    return dcc.Graph(figure=fig)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Trading Analytics", className="mb-4"),
            html.P("Deep dive into your trading performance", className="text-muted")
        ])
    ]),
    
    # Time Period Selector
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Analysis Period", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("From Date"),
                            dbc.Input(id="analytics-date-from", type="date")
                        ], width=6),
                        dbc.Col([
                            dbc.Label("To Date"),
                            dbc.Input(id="analytics-date-to", type="date")
                        ], width=6)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            html.Div(id="analytics-metrics")
        ])
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            html.Div(id="symbol-performance-chart")
        ], width=6),
        dbc.Col([
            html.Div(id="monthly-performance-chart")
        ], width=6)
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            html.Div(id="win-loss-chart")
        ], width=4),
        dbc.Col([
            html.Div(id="duration-analysis-chart")
        ], width=4),
        dbc.Col([
            html.Div(id="drawdown-chart")
        ], width=4)
    ], className="mb-4"),
    
    # Statistics Table
    dbc.Row([
        dbc.Col([
            html.H3("Detailed Statistics", className="mb-3"),
            html.Div(id="statistics-table")
        ])
    ])
], fluid=True)

@callback(
    [Output("analytics-metrics", "children"),
     Output("symbol-performance-chart", "children"),
     Output("monthly-performance-chart", "children"),
     Output("win-loss-chart", "children"),
     Output("duration-analysis-chart", "children"),
     Output("drawdown-chart", "children"),
     Output("statistics-table", "children")],
    [Input("analytics-date-from", "value"),
     Input("analytics-date-to", "value")]
)
def update_analytics(date_from: str, date_to: str) -> tuple:
    """Update analytics based on date range"""
    try:
        # Get filtered data
        df = get_trades_dataframe()
        
        if date_from:
            df = df[df['created_at'] >= date_from]
        if date_to:
            df = df[df['created_at'] <= date_to]
        
        if df.empty:
            empty_message = dbc.Alert("No data available for selected period.", color="info")
            return (empty_message,) * 7
        
        # Calculate analytics
        symbol_perf = get_symbol_performance(df)
        monthly_perf = get_monthly_performance(df)
        win_loss_dist = get_win_loss_distribution(df)
        duration_analysis = get_trade_duration_analysis(df)
        drawdown_data = get_drawdown_analysis(df)
        
        # Create metrics cards
        total_trades = len(df)
        total_pnl = df['total_pnl'].sum() if 'total_pnl' in df.columns else 0
        win_trades = len(df[df['status'] == 'WIN']) if 'status' in df.columns else 0
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        
        metrics = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${total_pnl:,.2f}", className="text-primary"),
                        html.P("Total P&L")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{win_rate:.1f}%", className="text-success"),
                        html.P("Win Rate")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(total_trades), className="text-info"),
                        html.P("Total Trades")
                    ])
                ], className="text-center")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${total_pnl/total_trades:,.2f}" if total_trades > 0 else "$0.00", className="text-warning"),
                        html.P("Avg Trade")
                    ])
                ], className="text-center")
            ], width=3)
        ])
        
        # Create charts
        symbol_chart = create_performance_chart(symbol_perf, "Performance by Symbol")
        monthly_chart = create_performance_chart(monthly_perf, "Monthly Performance")
        win_loss_chart = create_win_loss_pie(win_loss_dist.get('win_rate', 0), 
                                           win_loss_dist.get('loss_rate', 0))
        
        # Duration analysis chart
        duration_fig = go.Figure()
        if duration_analysis and 'avg_duration' in duration_analysis:
            duration_fig.add_trace(go.Bar(
                x=['Avg Duration'],
                y=[duration_analysis['avg_duration']],
                name='Duration (hours)'
            ))
        duration_fig.update_layout(title="Average Trade Duration", height=400)
        duration_chart = dcc.Graph(figure=duration_fig)
        
        # Drawdown chart
        drawdown_chart = create_drawdown_chart(drawdown_data)
        
        # Statistics table
        stats_data = [
            ["Metric", "Value"],
            ["Total Trades", total_trades],
            ["Winning Trades", win_trades],
            ["Losing Trades", total_trades - win_trades],
            ["Win Rate", f"{win_rate:.2f}%"],
            ["Total P&L", f"${total_pnl:,.2f}"],
            ["Average Trade", f"${total_pnl/total_trades:,.2f}" if total_trades > 0 else "$0.00"]
        ]
        
        stats_table = dbc.Table(
            [html.Thead([html.Tr([html.Th(stats_data[0][0]), html.Th(stats_data[0][1])])]),
             html.Tbody([html.Tr([html.Td(row[0]), html.Td(row[1])]) for row in stats_data[1:]])],
            striped=True, bordered=True, hover=True
        )
        
        return (metrics, symbol_chart, monthly_chart, win_loss_chart, 
                duration_chart, drawdown_chart, stats_table)
        
    except Exception as e:
        error_msg = dbc.Alert(f"Error loading analytics: {str(e)}", color="danger")
        return (error_msg,) * 7
