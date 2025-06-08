"""
Layout utilities for the TradeCraft application.

This module provides reusable layout components and utilities for consistent
page structure and responsive design.
"""
from typing import List, Optional, Any
import dash_bootstrap_components as dbc
from dash import html


def create_page_header(
    title: str,
    subtitle: Optional[str] = None,
    breadcrumbs: Optional[List[str]] = None
) -> dbc.Row:
    """
    Create a standardized page header with title and optional breadcrumbs.
    
    Args:
        title: Main page title
        subtitle: Optional subtitle text
        breadcrumbs: Optional list of breadcrumb items
        
    Returns:
        dbc.Row: Bootstrap row containing the page header
    """
    header_content = [
        html.H1(title, className="mb-2"),
    ]
    
    if subtitle:
        header_content.append(
            html.P(subtitle, className="text-muted mb-3")
        )
    
    if breadcrumbs:
        breadcrumb_items = []
        for i, crumb in enumerate(breadcrumbs):
            if i == len(breadcrumbs) - 1:
                # Last item is active
                breadcrumb_items.append(
                    dbc.BreadcrumbItem(crumb, active=True)
                )
            else:
                breadcrumb_items.append(
                    dbc.BreadcrumbItem(crumb, href="#")
                )
        
        header_content.insert(0, dbc.Breadcrumb(breadcrumb_items))
    
    return dbc.Row([
        dbc.Col(header_content, width=12)
    ], className="mb-4")


def create_metric_row(metrics: List[Any]) -> dbc.Row:
    """
    Create a responsive row of metric cards.
    
    Args:
        metrics: List of metric card components
        
    Returns:
        dbc.Row: Bootstrap row with metric cards
    """
    cols = []
    col_width = 12 // len(metrics) if len(metrics) <= 4 else 3
    
    for metric in metrics:
        cols.append(
            dbc.Col(
                metric,
                width=12,
                sm=6,
                md=col_width,
                className="mb-3"
            )
        )
    
    return dbc.Row(cols, className="mb-4")


def create_chart_grid(charts: List[Any], columns: int = 2) -> List[dbc.Row]:
    """
    Create a grid layout for charts.
    
    Args:
        charts: List of chart components
        columns: Number of columns in the grid
        
    Returns:
        List[dbc.Row]: List of bootstrap rows containing charts
    """
    rows = []
    col_width = 12 // columns
    
    for i in range(0, len(charts), columns):
        chart_batch = charts[i:i + columns]
        cols = []
        
        for chart in chart_batch:
            cols.append(
                dbc.Col(
                    chart,
                    width=12,
                    md=col_width,
                    className="mb-4"
                )
            )
        
        rows.append(dbc.Row(cols))
    
    return rows


def create_sidebar_layout(
    sidebar_content: Any,
    main_content: Any,
    sidebar_width: int = 3
) -> dbc.Row:
    """
    Create a sidebar layout with main content area.
    
    Args:
        sidebar_content: Content for the sidebar
        main_content: Content for the main area
        sidebar_width: Width of sidebar in Bootstrap columns (1-11)
        
    Returns:
        dbc.Row: Bootstrap row with sidebar and main content
    """
    main_width = 12 - sidebar_width
    
    return dbc.Row([
        dbc.Col(
            sidebar_content,
            width=12,
            md=sidebar_width,
            className="mb-4"
        ),
        dbc.Col(
            main_content,
            width=12,
            md=main_width
        )
    ])


def create_tabs_layout(
    tabs: List[dict],
    tab_content: Any,
    active_tab: str = "tab-1"
) -> dbc.Card:
    """
    Create a tabbed layout component.
    
    Args:
        tabs: List of tab dictionaries with 'label' and 'tab_id' keys
        tab_content: Content to display in tabs
        active_tab: ID of the initially active tab
        
    Returns:
        dbc.Card: Bootstrap card with tabbed interface
    """
    tab_list = []
    for tab in tabs:
        tab_list.append(
            dbc.Tab(
                label=tab['label'],
                tab_id=tab['tab_id']
            )
        )
    
    return dbc.Card([
        dbc.Tabs(
            tab_list,
            id="tabs",
            active_tab=active_tab
        ),
        dbc.CardBody(tab_content)
    ])


def create_filter_bar(filters: List[Any]) -> dbc.Card:
    """
    Create a filter bar component for data filtering.
    
    Args:
        filters: List of filter components (dropdowns, inputs, etc.)
        
    Returns:
        dbc.Card: Bootstrap card containing filter components
    """
    filter_cols = []
    for filter_component in filters:
        filter_cols.append(
            dbc.Col(
                filter_component,
                width=12,
                md=6,
                lg=3,
                className="mb-2"
            )
        )
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row(filter_cols)
        ])
    ], className="mb-4")
