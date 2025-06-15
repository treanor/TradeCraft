"""
Analytics Layout Module

Defines the UI layout for the analytics page.
This is the View layer in MVVM pattern - purely presentational.
"""
from dash import html, dcc
from components.filters import user_account_dropdowns


def create_analytics_layout() -> html.Div:
    """
    Create and return the complete analytics page layout.
    
    Returns:
        html.Div: The complete analytics page layout
    """
    return html.Div([
        # Data store for analytics
        dcc.Store(id="analytics-data-store"),
        
        # Header section
        _create_header_section(),
        
        # Summary statistics
        _create_summary_stats_section(),
        
        # P&L curve chart
        _create_pnl_chart_section(),
        
        # Analysis grid (allocation, tags, symbols)
        _create_analysis_grid(),
    ])


def _create_header_section() -> html.Div:
    """Create the header section with account dropdown."""
    return html.Div(
        [html.Div(
            user_account_dropdowns(), 
            style={
                "marginRight": "18px", 
                "maxWidth": "260px", 
                "flex": "0 0 260px"
            }
        )],
        className="d-flex align-items-start justify-content-between",
        style={
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "flex-start",
            "justifyContent": "space-between",
            "marginBottom": "18px",
            "gap": "18px",
            "width": "100%"
        },
    )


def _create_summary_stats_section() -> html.Div:
    """Create the summary statistics section."""
    return html.Div(
        id="analytics-summary-stats", 
        className="stats", 
        style={
            "marginBottom": "24px", 
            "width": "100%"
        }
    )


def _create_pnl_chart_section() -> html.Div:
    """Create the P&L curve chart section."""
    return html.Div([
        dcc.Graph(
            id="analytics-pnl-curve", 
            style={
                "background": "#23273A", 
                "borderRadius": "16px",
                "boxShadow": "0 2px 16px #00FFCC33", 
                "padding": "12px"
            }
        ),
    ], className="card", style={"marginBottom": "24px"})


def _create_analysis_grid() -> html.Div:
    """Create the analysis grid with asset allocation, tags, and symbols."""
    return html.Div([
        # Asset Allocation Chart
        html.Div([
            html.H4(
                "Asset Allocation", 
                className="section-title", 
                style={
                    "fontSize": "1.3rem", 
                    "marginBottom": "12px"
                }
            ),
            dcc.Graph(
                id="asset-allocation-chart", 
                style={
                    "background": "#23273A", 
                    "borderRadius": "16px",
                    "boxShadow": "0 2px 16px #00FFCC33", 
                    "padding": "12px"
                }
            ),
        ], className="card", style={
            "marginBottom": "24px", 
            "minWidth": "340px", 
            "flex": "1 1 340px"
        }),
        
        # PnL by Tag
        html.Div([
            html.H4(
                "PnL by Tag", 
                className="section-title", 
                style={
                    "fontSize": "1.3rem", 
                    "marginBottom": "12px"
                }
            ),
            html.Div(id="tag-table-container"),
        ], className="card", style={
            "marginBottom": "24px", 
            "minWidth": "340px", 
            "flex": "1 1 340px"
        }),
        
        # PnL by Symbol
        html.Div([
            html.H4(
                "PnL by Symbol", 
                className="section-title", 
                style={
                    "fontSize": "1.3rem", 
                    "marginBottom": "12px"
                }
            ),
            html.Div(id="symbol-table-container"),
        ], className="card", style={
            "marginBottom": "24px", 
            "minWidth": "340px", 
            "flex": "1 1 340px"
        }),
    ], style={
        "display": "flex", 
        "flexWrap": "wrap", 
        "gap": "24px", 
        "width": "100%"
    })
