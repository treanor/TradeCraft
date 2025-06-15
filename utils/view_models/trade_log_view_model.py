"""
Trade Log ViewModel

Handles business logic and data transformation for the trade log view.
Bridges between the data models and the UI components.
"""
from typing import Optional, Dict, Any, List
import pandas as pd
from utils import db_access
from utils.filters import apply_trade_filters, normalize_tags_column


class TradeLogViewModel:
    """
    ViewModel for trade log functionality.
    
    Handles data retrieval, filtering, and transformation for the trade log view.
    """
    
    def get_filtered_trades_data(
        self,
        account_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        symbols: Optional[List[str]] = None,
    ) -> str:
        """
        Fetch and filter trades based on the specified filters.
        
        This follows MVVM principles - the ViewModel handles data logic,
        while the View just displays whatever data it receives.
        
        Args:
            account_id: Account ID to filter by (optional - if None, shows all accounts)
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            tags: List of tags to filter by
            symbols: List of symbols to filter by
            
        Returns:
            JSON string representation of filtered trades DataFrame
        """
        # Fetch trade data based on account selection
        if account_id:
            # If account is selected, fetch trades for that account
            trades = db_access.fetch_trades_for_account(account_id)
        else:
            # If no account selected, fetch all trades
            trades = db_access.fetch_all_trades()
            
        df = pd.DataFrame(trades)
        
        if df.empty:
            return df.to_json(date_format="iso", orient="split")
            
        # Apply filters (ViewModel layer handles business logic)
        df = normalize_tags_column(df)
        df = apply_trade_filters(df, start_date, end_date, tags or [], symbols or [])
        
        # Enrich with analytics
        df = self._enrich_with_analytics(df)
        
        # Format for UI
        df = self._format_for_ui(df)
        
        return df.to_json(date_format="iso", orient="split")
    
    def _enrich_with_analytics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich DataFrame with calculated analytics for each trade.
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            DataFrame enriched with analytics data
        """
        if df.empty:
            return df
            
        analytics_list = []
        for _, trade in df.iterrows():
            analytics = db_access.trade_analytics(trade['id'])
            analytics_list.append(analytics)
        
        # Add calculated fields to the DataFrame
        analytics_df = pd.DataFrame(analytics_list)
        df['return_dollar'] = analytics_df['realized_pnl']
        df['status'] = analytics_df['status']
        df['total_fees'] = analytics_df['total_fees']
        df['open_qty'] = analytics_df['open_qty']
        df['avg_buy_price'] = analytics_df['avg_buy_price']
        df['avg_sell_price'] = analytics_df['avg_sell_price']
        
        return df
    
    def _format_for_ui(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format DataFrame fields for UI display.
        
        Args:
            df: DataFrame with enriched trade data
            
        Returns:
            DataFrame formatted for UI display
        """
        if df.empty:
            return df
            
        # Create 'date' column from opened_at/closed_at
        df['date'] = df['closed_at'].fillna(df['opened_at'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
          # Rename asset_symbol to symbol for UI
        df['symbol'] = df['asset_symbol']
        
        # Calculate additional fields needed by UI
        # Note: analytics data is already added in _enrich_with_analytics
        df['quantity'] = df['open_qty']  # Use open_qty from analytics
        df['entry_price'] = df['avg_buy_price']
        df['exit_price'] = df['avg_sell_price']
        
        # Calculate return percentage
        df['return_pct'] = self._calculate_return_percentage(df)
        
        # Calculate hold time
        df['hold_time'] = self._calculate_hold_time(df)
        
        # Add icon columns
        df['notes_icon'] = df['notes'].apply(lambda x: '📝' if x and str(x).strip() else '')
        df['tags_icon'] = df['tags'].apply(lambda x: '🏷️' if x and str(x).strip() else '')
        
        return df
    
    def _calculate_return_percentage(self, df: pd.DataFrame) -> pd.Series:
        """Calculate return percentage for trades."""
        return_pct = ((df['exit_price'] - df['entry_price']) / df['entry_price'] * 100).round(2)
        return return_pct.fillna(0)  # For open trades
    
    def _calculate_hold_time(self, df: pd.DataFrame) -> pd.Series:
        """Calculate hold time for trades."""
        def calc_hold_time(row: pd.Series) -> str:
            if row['closed_at']:
                days = (pd.to_datetime(row['closed_at']) - pd.to_datetime(row['opened_at'])).days
                return f"{days} days"
            return "Open"
        
        return df.apply(calc_hold_time, axis=1)
    
    def get_summary_stats(self, trades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics for trades.
        
        Args:
            trades_data: List of trade dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not trades_data:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }
        
        df = pd.DataFrame(trades_data)
        
        # Filter for closed trades only
        closed_trades = df[df['status'].isin(['Win', 'Loss'])]
        
        if closed_trades.empty:
            return {
                'total_trades': len(df),
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }
        
        winning_trades = closed_trades[closed_trades['status'] == 'Win']
        losing_trades = closed_trades[closed_trades['status'] == 'Loss']
        
        return {
            'total_trades': len(df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(closed_trades) * 100 if len(closed_trades) > 0 else 0,
            'total_pnl': closed_trades['return_dollar'].sum(),
            'avg_win': winning_trades['return_dollar'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['return_dollar'].mean() if len(losing_trades) > 0 else 0
        }
    
    def _apply_filters(
        self,
        df: pd.DataFrame, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        symbols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Apply filters to DataFrame - delegated to utility function."""
        return apply_trade_filters(df, start_date, end_date, tags, symbols)
    
    def _format_hold_time(self, opened_at: str, closed_at: str) -> str:
        """Format hold time for display."""
        if not opened_at:
            return "-"
        if not closed_at:
            return "Open"
        
        days = (pd.to_datetime(closed_at) - pd.to_datetime(opened_at)).days
        if days == 0:
            hours = (pd.to_datetime(closed_at) - pd.to_datetime(opened_at)).total_seconds() / 3600
            return f"{hours:.1f}h"
        return f"{days} days"
