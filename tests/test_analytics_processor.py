"""
Unit tests for analytics data processor.
"""
import pytest
import pandas as pd
from pages.analytics.data_processor import AnalyticsDataProcessor


@pytest.mark.unit
class TestAnalyticsDataProcessor:
    """Test analytics data processing functions."""
    
    @pytest.fixture
    def sample_trades_df(self):
        """Sample DataFrame with trade data."""
        return pd.DataFrame([
            {
                'id': 1,
                'asset_symbol': 'AAPL',
                'asset_type': 'stock',
                'status': 'WIN',
                'realized_pnl': 150.0,
                'return_pct': 5.2,
                'quantity': 100,
                'opened_at': '2024-01-15',
                'closed_at': '2024-01-20'
            },
            {
                'id': 2,
                'asset_symbol': 'GOOGL',
                'asset_type': 'stock',
                'status': 'LOSS',
                'realized_pnl': -75.0,
                'return_pct': -3.1,
                'quantity': 50,
                'opened_at': '2024-01-10',
                'closed_at': '2024-01-18'
            },
            {
                'id': 3,
                'asset_symbol': 'MSFT',
                'asset_type': 'stock',
                'status': 'OPEN',
                'realized_pnl': 0.0,
                'return_pct': 0.0,
                'quantity': 75,
                'opened_at': '2024-01-22',
                'closed_at': None
            }
        ])
    
    def test_process_filtered_data_empty(self):
        """Test processing empty data."""
        result = AnalyticsDataProcessor.process_filtered_data("")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_process_filtered_data_valid(self, sample_trades_df):
        """Test processing valid JSON data."""
        json_data = sample_trades_df.to_json(orient="split")
        result = AnalyticsDataProcessor.process_filtered_data(json_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == list(sample_trades_df.columns)
    
    def test_calculate_summary_stats(self, sample_trades_df):
        """Test summary statistics calculation."""
        stats = AnalyticsDataProcessor.calculate_summary_stats(sample_trades_df)
        
        assert isinstance(stats, list)
        assert len(stats) > 0
        
        # Should contain HTML components
        from dash import html
        assert all(isinstance(stat, html.Div) for stat in stats)
    
    def test_calculate_summary_stats_empty(self):
        """Test summary statistics with empty DataFrame."""
        empty_df = pd.DataFrame()
        stats = AnalyticsDataProcessor.calculate_summary_stats(empty_df)
        
        assert isinstance(stats, list)
        assert len(stats) == 1
        assert "No trades to summarize" in str(stats[0])
    
    def test_create_asset_allocation_figure(self, sample_trades_df):
        """Test asset allocation chart creation."""
        fig = AnalyticsDataProcessor.create_asset_allocation_figure(sample_trades_df)
        
        import plotly.graph_objs as go
        assert isinstance(fig, go.Figure)
        
        # Should have pie chart data
        assert len(fig.data) > 0
        assert fig.data[0].type == 'pie'
    
    def test_create_asset_allocation_figure_empty(self):
        """Test asset allocation with empty DataFrame."""
        empty_df = pd.DataFrame()
        fig = AnalyticsDataProcessor.create_asset_allocation_figure(empty_df)
        
        import plotly.graph_objs as go
        assert isinstance(fig, go.Figure)
    
    def test_calculate_max_streak(self, sample_trades_df):
        """Test max streak calculation."""
        # Create a winning streak
        win_series = pd.Series([True, True, False, True, True, True, False])
        win_streak = AnalyticsDataProcessor._calculate_max_streak(win_series)
        assert win_streak == 3  # Longest consecutive True values
        
        # Test losing streak
        loss_series = pd.Series([False, False, False, True, False, False])
        loss_streak = AnalyticsDataProcessor._calculate_max_streak(loss_series)
        assert loss_streak == 3
    
    def test_calculate_hold_times(self, sample_trades_df):
        """Test hold time calculations."""
        avg_win_hold, avg_loss_hold = AnalyticsDataProcessor._calculate_hold_times(sample_trades_df)
        
        assert isinstance(avg_win_hold, str)
        assert isinstance(avg_loss_hold, str)
        assert "day" in avg_win_hold.lower()
        assert "day" in avg_loss_hold.lower()
    
    def test_create_tag_table(self, sample_trades_df):
        """Test tag table creation."""
        # Add some tags to the sample data
        sample_trades_df['tags'] = ['momentum,tech', 'earnings,tech', 'value']
        
        table = AnalyticsDataProcessor.create_tag_table(sample_trades_df)
        
        from dash import html, dash_table
        assert isinstance(table, (html.Div, dash_table.DataTable, type(None)))
    
    def test_create_symbol_table(self, sample_trades_df):
        """Test symbol table creation."""
        table = AnalyticsDataProcessor.create_symbol_table(sample_trades_df)
        
        from dash import html, dash_table
        assert isinstance(table, (html.Div, dash_table.DataTable, type(None)))
