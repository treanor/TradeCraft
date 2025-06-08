"""
TradeCraft UI Components Package

This package contains reusable UI components and layout utilities for the
TradeCraft trading journal application. Components follow Bootstrap design
patterns and maintain consistent styling across the application.

Available modules:
- ui_components: Metric cards, charts, tables, alerts, and loading spinners
- layout_utils: Page headers, grids, sidebars, tabs, and filter bars
"""

# Import commonly used components for easy access
from .ui_components import (
    create_metric_card,
    create_chart_card,
    create_data_table_card,
    create_alert_component,
    create_loading_spinner
)

from .layout_utils import (
    create_page_header,
    create_metric_row,
    create_chart_grid,
    create_sidebar_layout,
    create_tabs_layout,
    create_filter_bar
)

__all__ = [
    # UI Components
    'create_metric_card',
    'create_chart_card', 
    'create_data_table_card',
    'create_alert_component',
    'create_loading_spinner',
    
    # Layout Utils
    'create_page_header',
    'create_metric_row',
    'create_chart_grid',
    'create_sidebar_layout',
    'create_tabs_layout',
    'create_filter_bar'
]
