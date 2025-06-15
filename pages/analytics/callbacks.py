"""
Analytics Callbacks Module

Handles all callback logic for the analytics page.
This is the ViewModel layer in MVVM pattern - handles user interactions and data flow.
"""
from typing import Any, Tuple
from dash import callback, Input, Output
from components.pnl_line_chart import pnl_over_time_figure
from .data_processor import AnalyticsDataProcessor


def register_analytics_callbacks() -> None:
    """Register all callbacks for the analytics page."""
    
    @callback(
        [
            Output("analytics-pnl-curve", "figure"),
            Output("analytics-summary-stats", "children"),
            Output("asset-allocation-chart", "figure"),
            Output("tag-table-container", "children"),
            Output("symbol-table-container", "children"),
        ],
        [Input("filtered-trades-store", "data")]
    )
    def update_analytics_from_filtered_store(data_json: Any) -> Tuple[Any, Any, Any, Any, Any]:
        """
        Update all analytics outputs from the global filtered DataFrame.
        
        Args:
            data_json: JSON string of filtered trades data
            
        Returns:
            Tuple containing all analytics components
        """
        # Process the data
        df = AnalyticsDataProcessor.process_filtered_data(data_json)
        
        # Generate all analytics components
        pnl_figure = pnl_over_time_figure(df)
        summary_stats = AnalyticsDataProcessor.calculate_summary_stats(df)
        asset_allocation = AnalyticsDataProcessor.create_asset_allocation_figure(df)
        tag_table = AnalyticsDataProcessor.create_tag_table(df)
        symbol_table = AnalyticsDataProcessor.create_symbol_table(df)
        
        return (
            pnl_figure,
            summary_stats,
            asset_allocation,
            tag_table,
            symbol_table,
        )
