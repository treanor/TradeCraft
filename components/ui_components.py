"""
Common UI components for the TradeCraft application.

This module provides reusable dashboard components following the DRY principle
and maintaining consistent styling across the application.
"""
from typing import Dict, Any, List, Optional, Union
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go


def create_metric_card(
    title: str, 
    value: Union[str, int, float], 
    icon: str = "bar-chart", 
    color: str = "primary",
    subtitle: Optional[str] = None
) -> dbc.Card:
    """
    Create a metric card component for displaying key statistics.
    
    Args:
        title: The title of the metric
        value: The metric value to display
        icon: Bootstrap icon name (without 'bi-' prefix)
        color: Bootstrap color variant
        subtitle: Optional subtitle text
        
    Returns:
        dbc.Card: Bootstrap card component with metric display
    """
    card_content = [
        dbc.CardBody([
            html.H4(
                [html.I(className=f"bi bi-{icon} me-2"), title],
                className="card-title text-muted"
            ),
            html.H2(str(value), className=f"text-{color} mb-0"),
            html.P(subtitle, className="text-muted small") if subtitle else None
        ])
    ]
    
    return dbc.Card(card_content, className="h-100")


def create_chart_card(
    title: str,
    figure: go.Figure,
    chart_id: str,
    height: int = 400
) -> dbc.Card:
    """
    Create a card component containing a Plotly chart.
    
    Args:
        title: Card title
        figure: Plotly figure object
        chart_id: Unique ID for the chart component
        height: Chart height in pixels
        
    Returns:
        dbc.Card: Bootstrap card with embedded chart
    """
    from dash import dcc
    
    return dbc.Card([
        dbc.CardHeader(html.H5(title, className="mb-0")),
        dbc.CardBody([
            dcc.Graph(
                id=chart_id,
                figure=figure,
                config={'displayModeBar': False},
                style={'height': f'{height}px'}
            )
        ])
    ], className="h-100")


def create_data_table_card(
    title: str,
    columns: List[Dict[str, Any]],
    data: List[Dict[str, Any]],
    table_id: str,
    page_size: int = 10
) -> dbc.Card:
    """
    Create a card component containing a data table.
    
    Args:
        title: Card title
        columns: Table column definitions
        data: Table data
        table_id: Unique ID for the table component
        page_size: Number of rows per page
        
    Returns:
        dbc.Card: Bootstrap card with embedded data table
    """
    from dash import dash_table
    
    return dbc.Card([
        dbc.CardHeader(html.H5(title, className="mb-0")),
        dbc.CardBody([
            dash_table.DataTable(
                id=table_id,
                columns=columns,
                data=data,
                page_size=page_size,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
        ])
    ], className="h-100")


def create_alert_component(
    message: str,
    alert_type: str = "info",
    dismissible: bool = True,
    alert_id: str = "alert"
) -> dbc.Alert:
    """
    Create an alert component for user notifications.
    
    Args:
        message: Alert message text
        alert_type: Bootstrap alert type (success, info, warning, danger)
        dismissible: Whether the alert can be dismissed
        alert_id: Unique ID for the alert component
        
    Returns:
        dbc.Alert: Bootstrap alert component
    """
    return dbc.Alert(
        message,
        color=alert_type,
        dismissable=dismissible,
        id=alert_id,
        is_open=True
    )


def create_loading_spinner(component_id: str, children: Any) -> dbc.Spinner:
    """
    Create a loading spinner wrapper for components.
    
    Args:
        component_id: ID for the spinner component
        children: Child components to wrap
        
    Returns:
        dbc.Spinner: Bootstrap spinner component
    """
    return dbc.Spinner(
        children,
        id=component_id,
        color="primary",
        type="border",
        fullscreen=False
    )
