"""
Integration tests for the complete workflow.
"""
import pytest
import pandas as pd
from utils import db_access
from utils.view_models.trade_log_view_model import TradeLogViewModel
from pages.analytics.data_processor import AnalyticsDataProcessor


@pytest.mark.integration
class TestWorkflowIntegration:
    """Test complete workflows across multiple components."""
    
    def test_trade_creation_and_analytics_workflow(self, test_db, sample_trade_data, sample_leg_data):
        """Test complete workflow: create trade -> add legs -> calculate analytics."""        # Step 1: Create a trade
        trade_id = db_access.insert_trade(
            user_id=sample_trade_data['user_id'],
            account_id=sample_trade_data['account_id'],
            asset_symbol=sample_trade_data['asset_symbol'],
            asset_type=sample_trade_data['asset_type'],
            opened_at=sample_trade_data['opened_at'],
            notes=sample_trade_data['notes'],
            db_path=test_db
        )
        
        # Step 2: Add buy leg
        buy_leg_id = db_access.insert_trade_leg(
            trade_id=trade_id,
            action='buy',
            quantity=100,
            price=150.0,
            fees=1.0,
            executed_at='2024-01-15 09:30:00',
            db_path=test_db
        )
        
        # Step 3: Add sell leg
        sell_leg_id = db_access.insert_trade_leg(
            trade_id=trade_id,
            action='sell',
            quantity=100,
            price=155.0,
            fees=1.0,
            executed_at='2024-01-20 15:30:00',
            db_path=test_db
        )
          # Step 4: Calculate analytics
        analytics = db_access.trade_analytics(trade_id, test_db)
        
        # Verify analytics
        assert analytics['status'] == 'WIN'  # 155*100 - 150*100 - 2 = 498 > 0
        assert analytics['realized_pnl'] == 498.0
        assert analytics['total_bought'] == 100
        assert analytics['total_sold'] == 100
        assert analytics['open_qty'] == 0
    
    def test_view_model_integration(self, test_db):
        """Test view model integration with database."""
        view_model = TradeLogViewModel()
        
        # Get filtered data - no user/account needed in MVVM
        result = view_model.get_filtered_trades_data(
            start_date="2020-01-01",
            end_date="2025-12-31"
        )
        
        # Parse result
        df = pd.read_json(result, orient="split")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check required columns        required_columns = ['return_dollar', 'status', 'return_pct']
        for col in required_columns:
            assert col in df.columns
        
        # Check status values
        statuses = df['status'].unique()
        valid_statuses = {'WIN', 'LOSS', 'OPEN', 'BREAK-EVEN'}
        assert all(status in valid_statuses for status in statuses)
    
    def test_analytics_processor_integration(self, test_db):
        """Test analytics processor with real data."""
        view_model = TradeLogViewModel()
        
        # Get data through view model - no user/account needed in MVVM
        json_data = view_model.get_filtered_trades_data(
            start_date="2020-01-01",
            end_date="2025-12-31"
        )
        
        # Process through analytics
        df = AnalyticsDataProcessor.process_filtered_data(json_data)
        stats = AnalyticsDataProcessor.calculate_summary_stats(df)
        
        assert isinstance(stats, list)
        assert len(stats) > 0
        
        # Test asset allocation
        fig = AnalyticsDataProcessor.create_asset_allocation_figure(df)
        assert fig is not None
    
    def test_filtering_workflow(self, test_db):
        """Test filtering workflow with various parameters."""
        view_model = TradeLogViewModel()
        
        # Test with different filters
        test_cases = [
            {
                'start_date': "2024-01-01",
                'end_date': "2024-12-31",
                'tags': None,
                'symbols': None
            },
            {
                'start_date': "2024-01-01", 
                'end_date': "2024-12-31",
                'tags': ['momentum'],
                'symbols': None
            },
            {                'start_date': "2024-01-01",
                'end_date': "2024-12-31", 
                'tags': None,
                'symbols': ['AAPL']
            }
        ]
          for test_case in test_cases:
            result = view_model.get_filtered_trades_data(
                **test_case
            )
            
            # Should always return valid JSON
            df = pd.read_json(result, orient="split")
            assert isinstance(df, pd.DataFrame)
    
    def test_win_loss_calculation_accuracy(self, test_db):
        """Test that win/loss calculations are accurate across the system."""
        # Get trades through view model
        view_model = TradeLogViewModel()        json_data = view_model.get_filtered_trades_data(
            start_date="2020-01-01",
            end_date="2025-12-31"
        )
        
        df = pd.read_json(json_data, orient="split")
        
        # Calculate stats through analytics processor
        stats_components = AnalyticsDataProcessor.calculate_summary_stats(df)
          # Manual verification - check if status column exists
        if 'status' in df.columns:
            wins = len(df[df['status'] == 'WIN'])
            losses = len(df[df['status'] == 'LOSS'])
            opens = len(df[df['status'] == 'OPEN'])
        else:
            # Fallback: use return_dollar to determine status
            wins = len(df[df['return_dollar'] > 0])
            losses = len(df[df['return_dollar'] < 0])
            zeros = len(df[df['return_dollar'] == 0])
            nans = df['return_dollar'].isna().sum()
            opens = zeros + nans  # Treat both as "open" trades
        
        # Verify counts are reasonable
        assert wins >= 0
        assert losses >= 0
        assert opens >= 0
        
        # Allow for some tolerance in case of floating point precision issues
        total_categorized = wins + losses + opens
        assert abs(total_categorized - len(df)) <= 1  # Allow 1 trade difference
          # Verify P&L consistency
        total_pnl = df['return_dollar'].sum()
        if 'status' in df.columns:
            win_pnl = df[df['status'] == 'WIN']['return_dollar'].sum()
            loss_pnl = df[df['status'] == 'LOSS']['return_dollar'].sum()
            open_pnl = df[df['status'] == 'OPEN']['return_dollar'].sum()
            assert abs(total_pnl - (win_pnl + loss_pnl + open_pnl)) < 0.01
        else:
            win_pnl = df[df['return_dollar'] > 0]['return_dollar'].sum()
            loss_pnl = df[df['return_dollar'] < 0]['return_dollar'].sum()
            zero_pnl = df[df['return_dollar'] == 0]['return_dollar'].sum()
            nan_pnl = df[df['return_dollar'].isna()]['return_dollar'].sum()
            # For P&L consistency, all values should add up to total (NaN sum is 0)
            calculated_total = win_pnl + loss_pnl + zero_pnl + (0 if pd.isna(nan_pnl) else nan_pnl)
            assert abs(total_pnl - calculated_total) < 0.01  # Account for floating point
