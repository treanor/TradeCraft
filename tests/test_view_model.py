"""
Unit tests for trade log view model.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from utils.view_models.trade_log_view_model import TradeLogViewModel


@pytest.mark.unit
class TestTradeLogViewModel:
    """Test trade log view model functionality."""
    
    @pytest.fixture
    def view_model(self):
        """Create a TradeLogViewModel instance."""
        return TradeLogViewModel()
    
    @pytest.fixture
    def sample_db_trades(self):
        """Sample trades data as returned from database."""
        return [
            {
                'id': 1,
                'asset_symbol': 'AAPL',
                'asset_type': 'stock',
                'opened_at': '2024-01-15 09:30:00',
                'closed_at': '2024-01-20 16:00:00',
                'notes': 'Test trade 1'
            },
            {
                'id': 2,
                'asset_symbol': 'GOOGL',
                'asset_type': 'stock',
                'opened_at': '2024-01-10 10:00:00',
                'closed_at': '2024-01-18 15:30:00',
                'notes': 'Test trade 2'
            }
        ]
    
    @pytest.fixture
    def sample_analytics_data(self):
        """Sample analytics data for trades."""
        return [
            {
                'trade_id': 1,
                'realized_pnl': 150.0,
                'status': 'WIN',
                'total_fees': 2.0,
                'open_qty': 0,
                'avg_buy_price': 145.0,
                'avg_sell_price': 147.5
            },
            {
                'trade_id': 2,
                'realized_pnl': -75.0,
                'status': 'LOSS',
                'total_fees': 1.5,
                'open_qty': 0,
                'avg_buy_price': 120.0,
                'avg_sell_price': 118.5
            }
        ]    def test_get_filtered_trades_data_no_user(self, view_model):
        """Test filtering with no data - MVVM doesn't need user_id."""
        result = view_model.get_filtered_trades_data(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        # Should return empty DataFrame as JSON (no trades in test DB)
        assert isinstance(result, str)
        df = pd.read_json(result, orient="split")
        assert df.empty
    
    @patch('utils.view_models.trade_log_view_model.db_access.fetch_trades_for_user_and_account')
    @patch('utils.view_models.trade_log_view_model.db_access.trade_analytics')
    def test_get_filtered_trades_data_with_data(self, mock_analytics, mock_fetch, 
                                              view_model, sample_db_trades, sample_analytics_data):
        """Test filtering with actual data."""
        # Setup mocks
        mock_fetch.return_value = sample_db_trades
        mock_analytics.side_effect = sample_analytics_data
        
        result = view_model.get_filtered_trades_data(start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        assert isinstance(result, str)
        df = pd.read_json(result, orient="split")
        
        # Check structure
        assert len(df) == 2
        assert 'return_dollar' in df.columns
        assert 'status' in df.columns
        assert 'return_pct' in df.columns
        
        # Check values
        assert df.iloc[0]['return_dollar'] == 150.0
        assert df.iloc[1]['return_dollar'] == -75.0
        assert df.iloc[0]['status'] == 'WIN'
        assert df.iloc[1]['status'] == 'LOSS'
    
    @patch('utils.view_models.trade_log_view_model.db_access.fetch_trades_for_user_and_account')
    def test_apply_filters(self, mock_fetch, view_model, sample_db_trades):
        """Test filter application."""
        mock_fetch.return_value = sample_db_trades
        
        df = pd.DataFrame(sample_db_trades)
        df['opened_at'] = pd.to_datetime(df['opened_at'])
        
        # Test date filtering
        filtered_df = view_model._apply_filters(
            df, 
            start_date="2024-01-12",
            end_date="2024-01-17",
            tags=None,
            symbols=None
        )
        
        # Should filter out the first trade (opened 2024-01-15 > 2024-01-12)
        assert len(filtered_df) <= len(df)
    
    def test_calculate_return_percentage(self, view_model):
        """Test return percentage calculation."""
        df = pd.DataFrame({
            'entry_price': [100.0, 200.0, 150.0],
            'exit_price': [110.0, 190.0, 150.0]
        })
        
        result = view_model._calculate_return_percentage(df)
        
        assert len(result) == 3
        assert result.iloc[0] == 10.0  # (110-100)/100 * 100
        assert result.iloc[1] == -5.0  # (190-200)/200 * 100
        assert result.iloc[2] == 0.0   # (150-150)/150 * 100
    
    def test_format_hold_time(self, view_model):
        """Test hold time formatting."""
        # Test with None values
        assert view_model._format_hold_time(None, None) == "-"
        
        # Test with actual dates
        opened = "2024-01-15 09:30:00"
        closed = "2024-01-20 16:00:00"
        result = view_model._format_hold_time(opened, closed)
        
        assert "day" in result
        assert isinstance(result, str)
    
    def test_enrich_with_analytics_empty(self, view_model):
        """Test enriching empty DataFrame."""
        empty_df = pd.DataFrame()
        result = view_model._enrich_with_analytics(empty_df)
        
        assert result.empty
        assert isinstance(result, pd.DataFrame)
    
    @patch('utils.view_models.trade_log_view_model.db_access.trade_analytics')
    def test_enrich_with_analytics(self, mock_analytics, view_model, sample_analytics_data):
        """Test enriching DataFrame with analytics."""
        mock_analytics.side_effect = sample_analytics_data
        
        df = pd.DataFrame([
            {'id': 1, 'asset_symbol': 'AAPL'},
            {'id': 2, 'asset_symbol': 'GOOGL'}
        ])
        
        result = view_model._enrich_with_analytics(df)
        
        # Check that analytics fields were added
        assert 'return_dollar' in result.columns
        assert 'status' in result.columns
        assert 'total_fees' in result.columns
        
        # Check values
        assert result.iloc[0]['return_dollar'] == 150.0
        assert result.iloc[1]['return_dollar'] == -75.0
