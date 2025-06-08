"""
Analytics utility functions for TradeCraft.
All functions use type hints and are documented.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


def get_dashboard_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key dashboard metrics from trades dataframe.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        Dictionary with dashboard metrics
    """
    if df.empty:
        return {
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'avg_return': 0.0
        }
    
    total_pnl = df['total_pnl'].sum() if 'total_pnl' in df.columns else 0.0
    total_trades = len(df)
    win_trades = len(df[df['status'] == 'WIN']) if 'status' in df.columns else 0
    win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0
    avg_return = total_pnl / total_trades if total_trades > 0 else 0.0
    
    return {
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'total_trades': total_trades,
        'avg_return': avg_return
    }


def get_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate equity curve from trades dataframe.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        DataFrame with date and cumulative P&L
    """
    if df.empty or 'total_pnl' not in df.columns:
        return pd.DataFrame(columns=['date', 'cumulative_pnl'])
    
    # Sort by date and calculate cumulative P&L
    df_sorted = df.sort_values('created_at').copy()
    df_sorted['cumulative_pnl'] = df_sorted['total_pnl'].cumsum()
    
    # Group by date to handle multiple trades per day
    daily_curve = df_sorted.groupby(df_sorted['created_at'].dt.date).agg({
        'cumulative_pnl': 'last'
    }).reset_index()
    
    daily_curve.columns = ['date', 'cumulative_pnl']
    return daily_curve


def get_daily_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily P&L from trades dataframe.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        DataFrame with date and daily P&L
    """
    if df.empty or 'total_pnl' not in df.columns:
        return pd.DataFrame(columns=['date', 'daily_pnl'])
    
    # Group by date and sum P&L
    daily_pnl = df.groupby(df['created_at'].dt.date).agg({
        'total_pnl': 'sum'
    }).reset_index()
    
    daily_pnl.columns = ['date', 'daily_pnl']
    return daily_pnl


def get_symbol_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate performance by symbol.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        DataFrame with symbol performance metrics
    """
    if df.empty or 'symbol' not in df.columns:
        return pd.DataFrame()
    
    symbol_stats = df.groupby('symbol').agg({
        'total_pnl': ['sum', 'count', 'mean'],
        'status': lambda x: (x == 'WIN').sum()
    }).round(2)
    
    # Flatten column names
    symbol_stats.columns = ['total_pnl', 'trade_count', 'avg_pnl', 'wins']
    symbol_stats['win_rate'] = (symbol_stats['wins'] / symbol_stats['trade_count'] * 100).round(1)
    
    return symbol_stats.sort_values('total_pnl', ascending=False)


def get_monthly_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly performance metrics.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        DataFrame with monthly performance
    """
    if df.empty or 'created_at' not in df.columns:
        return pd.DataFrame()
    
    df['year_month'] = df['created_at'].dt.to_period('M')
    
    monthly_stats = df.groupby('year_month').agg({
        'total_pnl': ['sum', 'count'],
        'status': lambda x: (x == 'WIN').sum()
    }).round(2)
    
    # Flatten column names
    monthly_stats.columns = ['total_pnl', 'trade_count', 'wins']
    monthly_stats['win_rate'] = (monthly_stats['wins'] / monthly_stats['trade_count'] * 100).round(1)
    
    return monthly_stats


def get_win_loss_distribution(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate win/loss distribution.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        Dictionary with win/loss rates
    """
    if df.empty or 'status' not in df.columns:
        return {'win_rate': 0.0, 'loss_rate': 0.0}
    
    total_trades = len(df)
    wins = len(df[df['status'] == 'WIN'])
    losses = len(df[df['status'] == 'LOSS'])
    
    return {
        'win_rate': (wins / total_trades * 100) if total_trades > 0 else 0.0,
        'loss_rate': (losses / total_trades * 100) if total_trades > 0 else 0.0
    }


def get_trade_duration_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze trade duration patterns.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        Dictionary with duration analysis
    """
    if df.empty:
        return {'avg_duration': 0, 'median_duration': 0}
    
    # For now, return placeholder data
    # This would need actual entry/exit times to calculate properly
    return {
        'avg_duration': 24,  # hours
        'median_duration': 12
    }


def get_drawdown_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate drawdown analysis from equity curve.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        DataFrame with drawdown data
    """
    if df.empty:
        return pd.DataFrame(columns=['date', 'drawdown'])
    
    equity_curve = get_equity_curve(df)
    
    if equity_curve.empty:
        return pd.DataFrame(columns=['date', 'drawdown'])
    
    # Calculate running maximum and drawdown
    equity_curve['running_max'] = equity_curve['cumulative_pnl'].expanding().max()
    equity_curve['drawdown'] = ((equity_curve['cumulative_pnl'] - equity_curve['running_max']) 
                               / equity_curve['running_max'] * 100)
    
    return equity_curve[['date', 'drawdown']]


def calculate_sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for the trading strategy.
    
    Args:
        df: DataFrame with trade data
        risk_free_rate: Annual risk-free rate (default 2%)
        
    Returns:
        Sharpe ratio
    """
    if df.empty or 'total_pnl' not in df.columns:
        return 0.0
    
    daily_returns = get_daily_pnl(df)['daily_pnl']
    
    if daily_returns.empty or daily_returns.std() == 0:
        return 0.0
    
    # Annualized return and volatility
    avg_daily_return = daily_returns.mean()
    daily_volatility = daily_returns.std()
    
    # Convert to annual (assuming 252 trading days)
    annual_return = avg_daily_return * 252
    annual_volatility = daily_volatility * np.sqrt(252)
    
    if annual_volatility == 0:
        return 0.0
    
    return (annual_return - risk_free_rate) / annual_volatility


def get_risk_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate various risk metrics.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        Dictionary with risk metrics
    """
    if df.empty:
        return {
            'max_drawdown': 0.0,
            'var_95': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0
        }
    
    # Calculate drawdown
    drawdown_data = get_drawdown_analysis(df)
    max_drawdown = abs(drawdown_data['drawdown'].min()) if not drawdown_data.empty else 0.0
    
    # Calculate VaR (95% confidence)
    daily_returns = get_daily_pnl(df)['daily_pnl']
    var_95 = abs(daily_returns.quantile(0.05)) if not daily_returns.empty else 0.0
    
    # Calculate Sharpe ratio
    sharpe = calculate_sharpe_ratio(df)
    
    # Calculate Sortino ratio (using downside deviation)
    negative_returns = daily_returns[daily_returns < 0]
    downside_deviation = negative_returns.std() * np.sqrt(252) if not negative_returns.empty else 0.0
    
    avg_return = daily_returns.mean() * 252 if not daily_returns.empty else 0.0
    sortino = (avg_return - 0.02) / downside_deviation if downside_deviation > 0 else 0.0
    
    return {
        'max_drawdown': max_drawdown,
        'var_95': var_95,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino
    }


def calculate_win_rate(df: pd.DataFrame) -> float:
    """
    Calculate win rate from trades dataframe.
    
    Args:
        df: DataFrame with trade data containing 'status' column
        
    Returns:
        Win rate as percentage (0-100)
    """
    if df.empty or 'status' not in df.columns:
        return 0.0
    
    win_trades = len(df[df['status'] == 'WIN'])
    total_trades = len(df[df['status'].isin(['WIN', 'LOSS'])])
    
    return (win_trades / total_trades * 100) if total_trades > 0 else 0.0


def calculate_total_pnl(df: pd.DataFrame) -> float:
    """
    Calculate total P&L from trades dataframe.
    
    Args:
        df: DataFrame with trade data containing 'total_pnl' column
        
    Returns:
        Total P&L amount
    """
    if df.empty or 'total_pnl' not in df.columns:
        return 0.0
    
    return float(df['total_pnl'].sum())


def calculate_avg_win_loss(df: pd.DataFrame) -> tuple[float, float]:
    """
    Calculate average win and loss amounts.
    
    Args:
        df: DataFrame with trade data
        
    Returns:
        Tuple of (average_win, average_loss)
    """
    if df.empty or 'total_pnl' not in df.columns or 'status' not in df.columns:
        return 0.0, 0.0
    
    wins = df[(df['status'] == 'WIN') & (df['total_pnl'] > 0)]['total_pnl']
    losses = df[(df['status'] == 'LOSS') & (df['total_pnl'] < 0)]['total_pnl']
    
    avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
    avg_loss = float(losses.mean()) if len(losses) > 0 else 0.0
    
    return avg_win, abs(avg_loss)  # Return absolute value for loss
