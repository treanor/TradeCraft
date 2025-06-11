"""
Advanced analytics utilities for Trade Craft.
Provides statistical calculations and performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from utils.exceptions import InsufficientDataError

@dataclass
class RiskMetrics:
    """Risk analysis metrics."""
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional Value at Risk 95%
    calmar_ratio: float

@dataclass
class PerformanceStats:
    """Comprehensive performance statistics."""
    total_return: float
    annualized_return: float
    volatility: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    expectancy: float

def calculate_returns_series(trades_df: pd.DataFrame) -> pd.Series:
    """
    Calculate daily returns series from trades DataFrame.
    
    Args:
        trades_df: DataFrame with trade data including 'opened_at' and 'realized_pnl'
    
    Returns:
        Pandas Series with daily returns
    """
    if trades_df.empty or 'realized_pnl' not in trades_df.columns:
        return pd.Series(dtype=float)
    
    # Convert to datetime and group by date
    trades_df = trades_df.copy()
    trades_df['opened_at'] = pd.to_datetime(trades_df['opened_at'])
    trades_df['date'] = trades_df['opened_at'].dt.date
    
    # Sum P&L by date
    daily_pnl = trades_df.groupby('date')['realized_pnl'].sum()
    
    # Convert to returns (assuming starting capital of $10,000)
    starting_capital = 10000
    cumulative_capital = starting_capital + daily_pnl.cumsum()
    returns = daily_pnl / cumulative_capital.shift(1, fill_value=starting_capital)
    
    return returns

def calculate_risk_metrics(returns: pd.Series, risk_free_rate: float = 0.02) -> RiskMetrics:
    """
    Calculate comprehensive risk metrics.
    
    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        RiskMetrics dataclass
    """
    if len(returns) < 30:
        raise InsufficientDataError("Need at least 30 data points for risk calculations")
    
    # Annualize risk-free rate to daily
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    
    # Basic metrics
    excess_returns = returns - daily_rf
    mean_return = returns.mean() * 252  # Annualized
    volatility = returns.std() * np.sqrt(252)  # Annualized
    
    # Sharpe Ratio
    sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    # Sortino Ratio (using downside deviation)
    downside_returns = returns[returns < 0]
    downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
    sortino_ratio = (mean_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
    
    # Drawdown calculations
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Max drawdown duration
    drawdown_duration = 0
    current_duration = 0
    for dd in drawdown:
        if dd < 0:
            current_duration += 1
            drawdown_duration = max(drawdown_duration, current_duration)
        else:
            current_duration = 0
    
    # Value at Risk (95%)
    var_95 = np.percentile(returns, 5)
    
    # Conditional Value at Risk (95%)
    cvar_95 = returns[returns <= var_95].mean()
    
    # Calmar Ratio
    calmar_ratio = mean_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    return RiskMetrics(
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        max_drawdown=max_drawdown,
        max_drawdown_duration=drawdown_duration,
        var_95=var_95,
        cvar_95=cvar_95,
        calmar_ratio=calmar_ratio
    )

def calculate_performance_stats(trades_df: pd.DataFrame) -> PerformanceStats:
    """
    Calculate comprehensive performance statistics.
    
    Args:
        trades_df: DataFrame with trade data
    
    Returns:
        PerformanceStats dataclass
    """
    if trades_df.empty or 'realized_pnl' not in trades_df.columns:
        return PerformanceStats(
            total_return=0, annualized_return=0, volatility=0, win_rate=0,
            profit_factor=0, avg_win=0, avg_loss=0, largest_win=0, largest_loss=0,
            consecutive_wins=0, consecutive_losses=0, expectancy=0
        )
    
    pnl_series = trades_df['realized_pnl'].dropna()
    
    if len(pnl_series) == 0:
        return PerformanceStats(
            total_return=0, annualized_return=0, volatility=0, win_rate=0,
            profit_factor=0, avg_win=0, avg_loss=0, largest_win=0, largest_loss=0,
            consecutive_wins=0, consecutive_losses=0, expectancy=0
        )
    
    # Basic stats
    total_return = pnl_series.sum()
    wins = pnl_series[pnl_series > 0]
    losses = pnl_series[pnl_series < 0]
    
    win_rate = len(wins) / len(pnl_series) if len(pnl_series) > 0 else 0
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    largest_win = wins.max() if len(wins) > 0 else 0
    largest_loss = losses.min() if len(losses) > 0 else 0
    
    # Profit factor
    gross_profit = wins.sum() if len(wins) > 0 else 0
    gross_loss = abs(losses.sum()) if len(losses) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Consecutive wins/losses
    consecutive_wins = consecutive_losses = 0
    current_wins = current_losses = 0
    
    for pnl in pnl_series:
        if pnl > 0:
            current_wins += 1
            current_losses = 0
            consecutive_wins = max(consecutive_wins, current_wins)
        elif pnl < 0:
            current_losses += 1
            current_wins = 0
            consecutive_losses = max(consecutive_losses, current_losses)
        else:
            current_wins = current_losses = 0
    
    # Expectancy
    expectancy = pnl_series.mean()
    
    # Time-based metrics
    if 'opened_at' in trades_df.columns:
        trades_df_copy = trades_df.copy()
        trades_df_copy['opened_at'] = pd.to_datetime(trades_df_copy['opened_at'])
        date_range = (trades_df_copy['opened_at'].max() - trades_df_copy['opened_at'].min()).days
        years = date_range / 365.25 if date_range > 0 else 1
        annualized_return = (total_return / 10000) / years if years > 0 else 0  # Assuming $10k starting capital
        
        # Calculate volatility from returns
        returns = calculate_returns_series(trades_df)
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
    else:
        annualized_return = 0
        volatility = 0
    
    return PerformanceStats(
        total_return=total_return,
        annualized_return=annualized_return,
        volatility=volatility,
        win_rate=win_rate,
        profit_factor=profit_factor,
        avg_win=avg_win,
        avg_loss=avg_loss,
        largest_win=largest_win,
        largest_loss=largest_loss,
        consecutive_wins=consecutive_wins,
        consecutive_losses=consecutive_losses,
        expectancy=expectancy
    )

def calculate_monthly_returns(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly returns for heatmap visualization.
    
    Args:
        trades_df: DataFrame with trade data
    
    Returns:
        DataFrame with monthly returns
    """
    if trades_df.empty or 'realized_pnl' not in trades_df.columns:
        return pd.DataFrame()
    
    trades_df = trades_df.copy()
    trades_df['opened_at'] = pd.to_datetime(trades_df['opened_at'])
    trades_df['year_month'] = trades_df['opened_at'].dt.to_period('M')
    
    monthly_returns = trades_df.groupby('year_month')['realized_pnl'].sum()
    
    # Convert to DataFrame with year and month columns
    result = monthly_returns.reset_index()
    result['year'] = result['year_month'].dt.year
    result['month'] = result['year_month'].dt.month
    result = result.drop('year_month', axis=1)
    
    return result

def calculate_trade_duration_stats(trades_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate statistics about trade durations.
    
    Args:
        trades_df: DataFrame with trade data including 'opened_at' and 'closed_at'
    
    Returns:
        Dictionary with duration statistics
    """
    if trades_df.empty or 'opened_at' not in trades_df.columns:
        return {}
    
    trades_df = trades_df.copy()
    trades_df['opened_at'] = pd.to_datetime(trades_df['opened_at'])
    
    # Only consider closed trades
    closed_trades = trades_df[trades_df['closed_at'].notna()].copy()
    if closed_trades.empty:
        return {}
    
    closed_trades['closed_at'] = pd.to_datetime(closed_trades['closed_at'])
    closed_trades['duration'] = closed_trades['closed_at'] - closed_trades['opened_at']
    closed_trades['duration_hours'] = closed_trades['duration'].dt.total_seconds() / 3600
    
    return {
        'avg_duration_hours': closed_trades['duration_hours'].mean(),
        'median_duration_hours': closed_trades['duration_hours'].median(),
        'min_duration_hours': closed_trades['duration_hours'].min(),
        'max_duration_hours': closed_trades['duration_hours'].max(),
        'std_duration_hours': closed_trades['duration_hours'].std()
    }

def calculate_symbol_performance(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate performance metrics by symbol.
    
    Args:
        trades_df: DataFrame with trade data
    
    Returns:
        DataFrame with symbol performance metrics
    """
    if trades_df.empty or 'symbol' not in trades_df.columns:
        return pd.DataFrame()
    
    symbol_stats = trades_df.groupby('symbol').agg({
        'realized_pnl': ['count', 'sum', 'mean', 'std'],
        'id': 'count'
    }).round(2)
    
    # Flatten column names
    symbol_stats.columns = ['trade_count', 'total_pnl', 'avg_pnl', 'pnl_std', 'trade_count_2']
    symbol_stats = symbol_stats.drop('trade_count_2', axis=1)
    
    # Calculate win rate by symbol
    win_rates = trades_df[trades_df['realized_pnl'] > 0].groupby('symbol').size() / trades_df.groupby('symbol').size()
    symbol_stats['win_rate'] = win_rates.fillna(0)
    
    # Calculate Sharpe-like ratio (avg return / std)
    symbol_stats['return_ratio'] = symbol_stats['avg_pnl'] / symbol_stats['pnl_std'].fillna(1)
    symbol_stats['return_ratio'] = symbol_stats['return_ratio'].fillna(0)
    
    return symbol_stats.reset_index()

def detect_trading_patterns(trades_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect patterns in trading behavior.
    
    Args:
        trades_df: DataFrame with trade data
    
    Returns:
        Dictionary with detected patterns
    """
    if trades_df.empty:
        return {}
    
    patterns = {}
    
    # Time-based patterns
    if 'opened_at' in trades_df.columns:
        trades_df = trades_df.copy()
        trades_df['opened_at'] = pd.to_datetime(trades_df['opened_at'])
        trades_df['hour'] = trades_df['opened_at'].dt.hour
        trades_df['day_of_week'] = trades_df['opened_at'].dt.day_name()
        
        # Best performing hours
        hourly_performance = trades_df.groupby('hour')['realized_pnl'].mean().sort_values(ascending=False)
        patterns['best_hours'] = hourly_performance.head(3).to_dict()
        patterns['worst_hours'] = hourly_performance.tail(3).to_dict()
        
        # Best performing days
        daily_performance = trades_df.groupby('day_of_week')['realized_pnl'].mean().sort_values(ascending=False)
        patterns['best_days'] = daily_performance.head(3).to_dict()
        patterns['worst_days'] = daily_performance.tail(3).to_dict()
    
    # Size-based patterns
    if 'quantity' in trades_df.columns:
        # Correlation between trade size and performance
        size_performance_corr = trades_df[['quantity', 'realized_pnl']].corr().iloc[0, 1]
        patterns['size_performance_correlation'] = size_performance_corr
    
    # Streak analysis
    if 'realized_pnl' in trades_df.columns:
        pnl_series = trades_df['realized_pnl']
        win_streaks = []
        loss_streaks = []
        current_streak = 0
        streak_type = None
        
        for pnl in pnl_series:
            if pnl > 0:
                if streak_type == 'win':
                    current_streak += 1
                else:
                    if streak_type == 'loss' and current_streak > 0:
                        loss_streaks.append(current_streak)
                    current_streak = 1
                    streak_type = 'win'
            elif pnl < 0:
                if streak_type == 'loss':
                    current_streak += 1
                else:
                    if streak_type == 'win' and current_streak > 0:
                        win_streaks.append(current_streak)
                    current_streak = 1
                    streak_type = 'loss'
        
        # Add final streak
        if streak_type == 'win' and current_streak > 0:
            win_streaks.append(current_streak)
        elif streak_type == 'loss' and current_streak > 0:
            loss_streaks.append(current_streak)
        
        patterns['avg_win_streak'] = np.mean(win_streaks) if win_streaks else 0
        patterns['avg_loss_streak'] = np.mean(loss_streaks) if loss_streaks else 0
        patterns['max_win_streak'] = max(win_streaks) if win_streaks else 0
        patterns['max_loss_streak'] = max(loss_streaks) if loss_streaks else 0
    
    return patterns