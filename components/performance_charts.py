"""
Reusable performance chart components for analytics.
"""
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np

def create_equity_curve(df: pd.DataFrame, title: str = "Equity Curve") -> go.Figure:
    """
    Create an equity curve chart from trade data.
    Args:
        df: DataFrame with trade data including 'opened_at' and 'realized_pnl' columns.
        title: Chart title.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative P&L ($)",
            template="plotly_white",
            height=400
        )
        return fig
    
    # Sort by date and calculate cumulative P&L
    df_sorted = df.sort_values('opened_at').copy()
    df_sorted['cum_pnl'] = df_sorted['realized_pnl'].fillna(0).cumsum()
    
    # Create the line chart
    fig = go.Figure()
    
    # Add equity curve line
    fig.add_trace(go.Scatter(
        x=df_sorted['opened_at'],
        y=df_sorted['cum_pnl'],
        mode='lines+markers',
        name='Equity Curve',
        line=dict(color='#2E86AB', width=2),
        marker=dict(size=4)
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Cumulative P&L ($)",
        template="plotly_white",
        height=400,
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

def create_drawdown_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a drawdown chart showing the decline from peak equity.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_sorted = df.sort_values('opened_at').copy()
    df_sorted['cum_pnl'] = df_sorted['realized_pnl'].fillna(0).cumsum()
    
    # Calculate running maximum (peak)
    df_sorted['peak'] = df_sorted['cum_pnl'].expanding().max()
    
    # Calculate drawdown
    df_sorted['drawdown'] = df_sorted['cum_pnl'] - df_sorted['peak']
    
    fig = go.Figure()
    
    # Add drawdown area
    fig.add_trace(go.Scatter(
        x=df_sorted['opened_at'],
        y=df_sorted['drawdown'],
        fill='tonexty',
        mode='lines',
        name='Drawdown',
        line=dict(color='#FF6B6B', width=1),
        fillcolor='rgba(255, 107, 107, 0.3)'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_color="black", line_width=1)
    
    fig.update_layout(
        title="Drawdown Chart",
        xaxis_title="Date",
        yaxis_title="Drawdown ($)",
        template="plotly_white",
        height=300,
        showlegend=False
    )
    
    return fig

def create_monthly_returns_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create a monthly returns heatmap.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_copy = df.copy()
    df_copy['opened_at'] = pd.to_datetime(df_copy['opened_at'])
    df_copy['year'] = df_copy['opened_at'].dt.year
    df_copy['month'] = df_copy['opened_at'].dt.month
    
    # Group by year and month
    monthly_returns = df_copy.groupby(['year', 'month'])['realized_pnl'].sum().reset_index()
    
    # Pivot for heatmap
    heatmap_data = monthly_returns.pivot(index='year', columns='month', values='realized_pnl')
    
    # Fill missing months with 0
    for month in range(1, 13):
        if month not in heatmap_data.columns:
            heatmap_data[month] = 0
    
    heatmap_data = heatmap_data.fillna(0)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=heatmap_data.index,
        colorscale='RdYlGn',
        zmid=0,
        text=heatmap_data.values,
        texttemplate="%{text:.0f}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Monthly Returns Heatmap",
        xaxis_title="Month",
        yaxis_title="Year",
        template="plotly_white",
        height=300
    )
    
    return fig

def create_win_loss_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create a histogram showing the distribution of wins and losses.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    # Filter out zero P&L trades
    pnl_data = df[df['realized_pnl'] != 0]['realized_pnl']
    
    if pnl_data.empty:
        return go.Figure()
    
    # Separate wins and losses
    wins = pnl_data[pnl_data > 0]
    losses = pnl_data[pnl_data < 0]
    
    fig = go.Figure()
    
    # Add histogram for wins
    if not wins.empty:
        fig.add_trace(go.Histogram(
            x=wins,
            name='Wins',
            marker_color='#4CAF50',
            opacity=0.7,
            nbinsx=20
        ))
    
    # Add histogram for losses
    if not losses.empty:
        fig.add_trace(go.Histogram(
            x=losses,
            name='Losses',
            marker_color='#F44336',
            opacity=0.7,
            nbinsx=20
        ))
    
    fig.update_layout(
        title="Win/Loss Distribution",
        xaxis_title="P&L ($)",
        yaxis_title="Frequency",
        template="plotly_white",
        height=300,
        barmode='overlay'
    )
    
    return fig

def create_performance_by_day_of_week(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing performance by day of week.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_copy = df.copy()
    df_copy['opened_at'] = pd.to_datetime(df_copy['opened_at'])
    df_copy['day_of_week'] = df_copy['opened_at'].dt.day_name()
    
    # Group by day of week
    day_performance = df_copy.groupby('day_of_week')['realized_pnl'].sum().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ], fill_value=0)
    
    # Create colors based on positive/negative values
    colors = ['#4CAF50' if val >= 0 else '#F44336' for val in day_performance.values]
    
    fig = go.Figure(data=go.Bar(
        x=day_performance.index,
        y=day_performance.values,
        marker_color=colors,
        text=[f'${val:.0f}' for val in day_performance.values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Performance by Day of Week",
        xaxis_title="Day",
        yaxis_title="Total P&L ($)",
        template="plotly_white",
        height=300,
        showlegend=False
    )
    
    return fig

def create_performance_by_hour(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing performance by hour of day.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_copy = df.copy()
    df_copy['opened_at'] = pd.to_datetime(df_copy['opened_at'])
    df_copy['hour'] = df_copy['opened_at'].dt.hour
    
    # Group by hour
    hour_performance = df_copy.groupby('hour')['realized_pnl'].sum().reindex(
        range(24), fill_value=0
    )
    
    # Create colors based on positive/negative values
    colors = ['#4CAF50' if val >= 0 else '#F44336' for val in hour_performance.values]
    
    fig = go.Figure(data=go.Bar(
        x=[f'{h:02d}:00' for h in hour_performance.index],
        y=hour_performance.values,
        marker_color=colors,
        text=[f'${val:.0f}' if val != 0 else '' for val in hour_performance.values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Performance by Hour",
        xaxis_title="Hour",
        yaxis_title="Total P&L ($)",
        template="plotly_white",
        height=300,
        showlegend=False
    )
    
    return fig

def create_risk_return_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Create a risk-return scatter plot for different symbols or strategies.
    Args:
        df: DataFrame with trade data.
    Returns:
        Plotly figure.
    """
    if df.empty or 'realized_pnl' not in df.columns or 'symbol' not in df.columns:
        return go.Figure()
    
    # Group by symbol and calculate metrics
    symbol_metrics = []
    for symbol in df['symbol'].unique():
        symbol_trades = df[df['symbol'] == symbol]['realized_pnl']
        if len(symbol_trades) > 1:  # Need at least 2 trades for std calculation
            avg_return = symbol_trades.mean()
            volatility = symbol_trades.std()
            trade_count = len(symbol_trades)
            symbol_metrics.append({
                'symbol': symbol,
                'avg_return': avg_return,
                'volatility': volatility,
                'trade_count': trade_count
            })
    
    if not symbol_metrics:
        return go.Figure()
    
    metrics_df = pd.DataFrame(symbol_metrics)
    
    fig = go.Figure(data=go.Scatter(
        x=metrics_df['volatility'],
        y=metrics_df['avg_return'],
        mode='markers+text',
        text=metrics_df['symbol'],
        textposition='top center',
        marker=dict(
            size=metrics_df['trade_count'] * 2,  # Size based on trade count
            color=metrics_df['avg_return'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Avg Return")
        )
    ))
    
    fig.update_layout(
        title="Risk-Return Analysis by Symbol",
        xaxis_title="Volatility (Std Dev)",
        yaxis_title="Average Return ($)",
        template="plotly_white",
        height=400
    )
    
    return fig