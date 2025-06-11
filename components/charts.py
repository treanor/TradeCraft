"""
Reusable chart components for Trade Craft.
Provides consistent styling and functionality across the application.
"""

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np
from utils.analytics import calculate_returns_series

# Define consistent color scheme
COLORS = {
    'primary': '#2E86AB',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'profit': '#00d68f',
    'loss': '#ff3860',
    'neutral': '#6c757d'
}

CHART_TEMPLATE = "plotly_white"
CHART_HEIGHT = 400

def create_equity_curve(
    df: pd.DataFrame, 
    title: str = "Equity Curve",
    height: int = CHART_HEIGHT
) -> go.Figure:
    """
    Create an enhanced equity curve chart with drawdown overlay.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative P&L ($)",
            template=CHART_TEMPLATE,
            height=height
        )
        return fig
    
    # Sort by date and calculate cumulative P&L
    df_sorted = df.sort_values('opened_at').copy()
    df_sorted['cum_pnl'] = df_sorted['realized_pnl'].fillna(0).cumsum()
    
    # Calculate drawdown
    df_sorted['peak'] = df_sorted['cum_pnl'].expanding().max()
    df_sorted['drawdown'] = df_sorted['cum_pnl'] - df_sorted['peak']
    
    # Create subplot with secondary y-axis
    fig = go.Figure()
    
    # Add equity curve
    fig.add_trace(go.Scatter(
        x=df_sorted['opened_at'],
        y=df_sorted['cum_pnl'],
        mode='lines',
        name='Equity Curve',
        line=dict(color=COLORS['primary'], width=2),
        hovertemplate='Date: %{x}<br>P&L: $%{y:,.2f}<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS['neutral'], opacity=0.5)
    
    # Add annotations for key metrics
    total_pnl = df_sorted['cum_pnl'].iloc[-1] if not df_sorted.empty else 0
    max_drawdown = df_sorted['drawdown'].min() if not df_sorted.empty else 0
    
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"Total P&L: ${total_pnl:,.2f}<br>Max Drawdown: ${max_drawdown:,.2f}",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor=COLORS['neutral'],
        borderwidth=1
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Cumulative P&L ($)",
        template=CHART_TEMPLATE,
        height=height,
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

def create_performance_heatmap(
    df: pd.DataFrame,
    title: str = "Monthly Returns Heatmap"
) -> go.Figure:
    """
    Create a monthly returns heatmap with enhanced styling.
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
    
    # Create custom colorscale
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=heatmap_data.index,
        colorscale=[
            [0, COLORS['loss']],
            [0.5, 'white'],
            [1, COLORS['profit']]
        ],
        zmid=0,
        text=heatmap_data.values,
        texttemplate="%{text:.0f}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='Year: %{y}<br>Month: %{x}<br>Return: $%{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Year",
        template=CHART_TEMPLATE,
        height=300
    )
    
    return fig

def create_win_loss_distribution(
    df: pd.DataFrame,
    title: str = "Win/Loss Distribution"
) -> go.Figure:
    """
    Create an enhanced win/loss distribution chart.
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
            marker_color=COLORS['profit'],
            opacity=0.7,
            nbinsx=20,
            hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
        ))
    
    # Add histogram for losses
    if not losses.empty:
        fig.add_trace(go.Histogram(
            x=losses,
            name='Losses',
            marker_color=COLORS['loss'],
            opacity=0.7,
            nbinsx=20,
            hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
        ))
    
    # Add vertical lines for means
    if not wins.empty:
        fig.add_vline(x=wins.mean(), line_dash="dash", 
                     line_color=COLORS['profit'], opacity=0.8,
                     annotation_text=f"Avg Win: ${wins.mean():.2f}")
    
    if not losses.empty:
        fig.add_vline(x=losses.mean(), line_dash="dash", 
                     line_color=COLORS['loss'], opacity=0.8,
                     annotation_text=f"Avg Loss: ${losses.mean():.2f}")
    
    fig.update_layout(
        title=title,
        xaxis_title="P&L ($)",
        yaxis_title="Frequency",
        template=CHART_TEMPLATE,
        height=300,
        barmode='overlay'
    )
    
    return fig

def create_performance_by_time(
    df: pd.DataFrame,
    time_grouping: str = "hour",
    title: str = None
) -> go.Figure:
    """
    Create performance chart grouped by time (hour, day of week, etc.).
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_copy = df.copy()
    df_copy['opened_at'] = pd.to_datetime(df_copy['opened_at'])
    
    if time_grouping == "hour":
        df_copy['time_group'] = df_copy['opened_at'].dt.hour
        x_labels = [f'{h:02d}:00' for h in range(24)]
        title = title or "Performance by Hour"
        xlabel = "Hour"
    elif time_grouping == "day_of_week":
        df_copy['time_group'] = df_copy['opened_at'].dt.day_name()
        x_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        title = title or "Performance by Day of Week"
        xlabel = "Day"
    else:
        raise ValueError("time_grouping must be 'hour' or 'day_of_week'")
    
    # Group by time and calculate metrics
    time_performance = df_copy.groupby('time_group').agg({
        'realized_pnl': ['sum', 'mean', 'count']
    }).round(2)
    
    time_performance.columns = ['total_pnl', 'avg_pnl', 'trade_count']
    
    # Reindex to ensure all time periods are included
    if time_grouping == "hour":
        time_performance = time_performance.reindex(range(24), fill_value=0)
    else:
        time_performance = time_performance.reindex(x_labels, fill_value=0)
    
    # Create colors based on performance
    colors = [COLORS['profit'] if val >= 0 else COLORS['loss'] 
              for val in time_performance['total_pnl']]
    
    fig = go.Figure()
    
    # Add total P&L bars
    fig.add_trace(go.Bar(
        x=x_labels if time_grouping == "day_of_week" else [f'{h:02d}:00' for h in range(24)],
        y=time_performance['total_pnl'],
        name='Total P&L',
        marker_color=colors,
        text=[f'${val:.0f}' if val != 0 else '' for val in time_performance['total_pnl']],
        textposition='auto',
        hovertemplate=f'{xlabel}: %{{x}}<br>Total P&L: $%{{y:,.2f}}<br>Avg P&L: $%{{customdata[0]:,.2f}}<br>Trades: %{{customdata[1]}}<extra></extra>',
        customdata=time_performance[['avg_pnl', 'trade_count']].values
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title="Total P&L ($)",
        template=CHART_TEMPLATE,
        height=300,
        showlegend=False
    )
    
    return fig

def create_drawdown_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a detailed drawdown chart.
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_sorted = df.sort_values('opened_at').copy()
    df_sorted['cum_pnl'] = df_sorted['realized_pnl'].fillna(0).cumsum()
    
    # Calculate running maximum (peak)
    df_sorted['peak'] = df_sorted['cum_pnl'].expanding().max()
    
    # Calculate drawdown
    df_sorted['drawdown'] = df_sorted['cum_pnl'] - df_sorted['peak']
    df_sorted['drawdown_pct'] = (df_sorted['drawdown'] / df_sorted['peak']) * 100
    
    fig = go.Figure()
    
    # Add drawdown area
    fig.add_trace(go.Scatter(
        x=df_sorted['opened_at'],
        y=df_sorted['drawdown'],
        fill='tonexty',
        mode='lines',
        name='Drawdown',
        line=dict(color=COLORS['loss'], width=1),
        fillcolor=f'rgba(255, 56, 96, 0.3)',
        hovertemplate='Date: %{x}<br>Drawdown: $%{y:,.2f}<br>Drawdown %: %{customdata:.1f}%<extra></extra>',
        customdata=df_sorted['drawdown_pct']
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_color="black", line_width=1)
    
    # Add annotation for max drawdown
    max_dd_idx = df_sorted['drawdown'].idxmin()
    max_dd_date = df_sorted.loc[max_dd_idx, 'opened_at']
    max_dd_value = df_sorted.loc[max_dd_idx, 'drawdown']
    
    fig.add_annotation(
        x=max_dd_date,
        y=max_dd_value,
        text=f"Max DD: ${max_dd_value:,.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLORS['loss'],
        bgcolor="white",
        bordercolor=COLORS['loss']
    )
    
    fig.update_layout(
        title="Drawdown Chart",
        xaxis_title="Date",
        yaxis_title="Drawdown ($)",
        template=CHART_TEMPLATE,
        height=300,
        showlegend=False
    )
    
    return fig

def create_rolling_metrics_chart(
    df: pd.DataFrame,
    window: int = 30,
    metric: str = "sharpe"
) -> go.Figure:
    """
    Create a rolling metrics chart (Sharpe ratio, win rate, etc.).
    """
    if df.empty or 'realized_pnl' not in df.columns:
        return go.Figure()
    
    df_sorted = df.sort_values('opened_at').copy()
    
    if metric == "sharpe":
        returns = calculate_returns_series(df_sorted)
        rolling_sharpe = returns.rolling(window=window).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        y_data = rolling_sharpe
        title = f"Rolling {window}-Day Sharpe Ratio"
        ylabel = "Sharpe Ratio"
    elif metric == "win_rate":
        df_sorted['is_win'] = (df_sorted['realized_pnl'] > 0).astype(int)
        rolling_win_rate = df_sorted['is_win'].rolling(window=window).mean() * 100
        y_data = rolling_win_rate
        title = f"Rolling {window}-Trade Win Rate"
        ylabel = "Win Rate (%)"
    else:
        raise ValueError("metric must be 'sharpe' or 'win_rate'")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_sorted['opened_at'],
        y=y_data,
        mode='lines',
        name=metric.title(),
        line=dict(color=COLORS['primary'], width=2),
        hovertemplate=f'Date: %{{x}}<br>{ylabel}: %{{y:.2f}}<extra></extra>'
    ))
    
    # Add reference lines
    if metric == "sharpe":
        fig.add_hline(y=1, line_dash="dash", line_color=COLORS['success'], 
                     annotation_text="Good (1.0)")
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS['neutral'])
    elif metric == "win_rate":
        fig.add_hline(y=50, line_dash="dash", line_color=COLORS['neutral'], 
                     annotation_text="50%")
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=ylabel,
        template=CHART_TEMPLATE,
        height=300,
        showlegend=False
    )
    
    return fig