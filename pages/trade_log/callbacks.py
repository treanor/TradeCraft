"""
Trade Log Callbacks Module

Handles all callback logic for the trade log page.
This is the ViewModel layer in MVVM pattern - handles user interactions and data flow.
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import date, timedelta
import pandas as pd
from dash import callback, Input, Output, State, ctx, dash, html
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
from utils import db_access
from config import get_default_user


def register_trade_log_callbacks() -> None:
    """Register all callbacks for the trade log page."""
    _register_table_callbacks()
    _register_navigation_callbacks()
    _register_chart_callbacks()
    _register_filter_callbacks()
    _register_modal_callbacks()


def _register_table_callbacks() -> None:
    """Register callbacks related to the trade table."""
    
    @callback(
        Output("trade-table", "data"),
        [Input("filtered-trades-store", "data")],
    )
    def update_trade_table_from_store(data_json: str) -> List[Dict[str, Any]]:
        """Update the trade log table from the global filtered DataFrame."""
        if not data_json:
            return []
        from io import StringIO
        df = pd.read_json(StringIO(data_json), orient="split")
        return df.to_dict("records")


def _register_navigation_callbacks() -> None:
    """Register callbacks for navigation."""
    
    @callback(
        Output("trade-log-navigate", "href"),
        Input("trade-table", "selected_rows"),
        State("trade-table", "data"),
        prevent_initial_call=True
    )
    def go_to_trade_detail(selected_rows: List[int], data: List[Dict[str, Any]]) -> str:
        """Navigate to trade detail page when a trade is selected."""
        if selected_rows:
            trade_id = data[selected_rows[0]]["id"]
            return f"/trade_detail/{trade_id}"
        return dash.no_update


def _register_chart_callbacks() -> None:
    """Register callbacks for charts and statistics."""
    
    @callback(
        [Output("equity-curve-chart", "figure"), Output("trade-log-summary-stats", "children")],
        [
            Input("trade-table", "data"),
            State("date-filter", "start_date"),
            State("date-filter", "end_date"),
        ],
    )
    def update_equity_and_stats(table_data: list[dict], start_date: str, end_date: str) -> tuple:
        """Update the equity curve chart and summary stats based on filtered trades."""
        import plotly.graph_objs as go
        
        if not table_data or len(table_data) == 0:
            fig = go.Figure()
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), template="plotly_white")
            stats = [html.Div("No trades to summarize.")]
            return fig, stats
        
        df = pd.DataFrame(table_data)
        
        # Create equity curve
        fig = _create_equity_curve_figure(df, start_date, end_date)
        
        # Create summary stats
        stats = _create_summary_stats(df)
        
        return fig, stats


def _register_filter_callbacks() -> None:
    """Register callbacks for filtering functionality."""
    
    @callback(
        Output("date-filter", "start_date"),
        Output("date-filter", "end_date"),
        [
            Input("quickfilter-today", "n_clicks"),
            Input("quickfilter-yesterday", "n_clicks"),
            Input("quickfilter-thisweek", "n_clicks"),
            Input("quickfilter-lastweek", "n_clicks"),
            Input("quickfilter-thismonth", "n_clicks"),
            Input("quickfilter-lastmonth", "n_clicks"),
            Input("quickfilter-alltime", "n_clicks"),
        ],
        prevent_initial_call=True
    )
    def set_quick_date_filter(
        today: Optional[int], 
        yesterday: Optional[int], 
        thisweek: Optional[int], 
        lastweek: Optional[int], 
        thismonth: Optional[int], 
        lastmonth: Optional[int], 
        alltime: Optional[int]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Set date filter based on quick filter buttons."""
        triggered = ctx.triggered_id
        today_dt = date.today()
        
        if triggered == "quickfilter-today":
            return today_dt.isoformat(), today_dt.isoformat()
        elif triggered == "quickfilter-yesterday":
            yest = today_dt - timedelta(days=1)
            return yest.isoformat(), yest.isoformat()
        elif triggered == "quickfilter-thisweek":
            start = today_dt - timedelta(days=today_dt.weekday())
            return start.isoformat(), today_dt.isoformat()
        elif triggered == "quickfilter-lastweek":
            start = today_dt - timedelta(days=today_dt.weekday() + 7)
            end = start + timedelta(days=6)
            return start.isoformat(), end.isoformat()
        elif triggered == "quickfilter-thismonth":
            start = today_dt.replace(day=1)
            return start.isoformat(), today_dt.isoformat()
        elif triggered == "quickfilter-lastmonth":
            if today_dt.month == 1:
                start = today_dt.replace(year=today_dt.year - 1, month=12, day=1)
                end = today_dt.replace(day=1) - timedelta(days=1)
            else:
                start = today_dt.replace(month=today_dt.month - 1, day=1)
                end = today_dt.replace(day=1) - timedelta(days=1)
            return start.isoformat(), end.isoformat()
        elif triggered == "quickfilter-alltime":
            return None, None
        
        return dash.no_update, dash.no_update

    @callback(
        Output("symbol-filter", "value", allow_duplicate=True),
        Output("tag-filter", "value", allow_duplicate=True),
        Output("date-filter", "start_date", allow_duplicate=True),
        Output("date-filter", "end_date", allow_duplicate=True),
        Input("clear-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_trade_log_filters(n_clicks: Optional[int]) -> Tuple[None, None, None, None]:
        """Clear all filters when clear button is clicked."""
        return None, None, None, None


def _register_modal_callbacks() -> None:
    """Register callbacks for the add trade modal."""
    
    @callback(
        Output("add-trade-modal", "is_open"),
        Output("add-legs-store", "data"),
        [
            Input("add-trade-btn", "n_clicks"),
            Input("add-trade-submit", "n_clicks"),
            Input("add-trade-cancel", "n_clicks"),
        ],
        [State("add-trade-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_add_trade_modal(
        add_btn: Optional[int], 
        submit_btn: Optional[int], 
        cancel_btn: Optional[int], 
        is_open: bool
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Toggle the add trade modal and initialize legs store."""
        if add_btn or submit_btn or cancel_btn:
            return not is_open, []
        return is_open, []

    @callback(
        Output("add-legs-table", "children"),
        [Input("add-legs-store", "data")],
        prevent_initial_call=True
    )
    def render_legs_table(legs: Optional[List[Dict[str, Any]]]) -> html.Div:
        """Render the legs table from the store."""
        if not legs:
            return html.Div("No legs. Add at least one leg.")
        
        rows = []
        for i, leg in enumerate(legs):
            rows.append(_create_leg_row(i, leg))
        
        return html.Div(rows)

    @callback(
        Output("add-legs-store", "data", allow_duplicate=True),
        Input("add-leg-btn", "n_clicks"),
        State("add-legs-store", "data"),
        prevent_initial_call=True
    )
    def add_leg(n_clicks: int, legs: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Add a new leg to the store."""
        if not legs:
            legs = []
        legs.append({
            "action": "BUY",
            "date": date.today().isoformat(),
            "time": "09:30",
            "quantity": 1,
            "price": 1.0,
            "fee": 0.0,
        })
        return legs

    @callback(
        Output("add-legs-store", "data", allow_duplicate=True),
        [
            Input({"type": "remove-leg-btn", "index": ALL}, "n_clicks")
        ],
        [State("add-legs-store", "data")],
        prevent_initial_call=True
    )
    def remove_leg(remove_clicks: List[Optional[int]], legs: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Remove a leg row when its remove button is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered or not legs:
            raise dash.exceptions.PreventUpdate
        for i, btn in enumerate(remove_clicks):
            if btn:
                legs.pop(i)
                break
        return legs

    @callback(
        Output("add-legs-store", "data", allow_duplicate=True),
        [
            Input({"type": "leg-action", "index": ALL}, "value"),
            Input({"type": "leg-date", "index": ALL}, "date"),
            Input({"type": "leg-time", "index": ALL}, "value"),
            Input({"type": "leg-quantity", "index": ALL}, "value"),
            Input({"type": "leg-price", "index": ALL}, "value"),
            Input({"type": "leg-fee", "index": ALL}, "value"),
        ],
        [State("add-legs-store", "data")],
        prevent_initial_call=True
    )
    def update_leg_fields(
        actions: List[str], 
        dates: List[str], 
        times: List[str], 
        quantities: List[int], 
        prices: List[float], 
        fees: List[float], 
        legs: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Update the legs store when any field in any leg row changes."""
        if not legs:
            raise dash.exceptions.PreventUpdate
        for i in range(len(legs)):
            legs[i]["action"] = actions[i]
            legs[i]["date"] = dates[i]
            legs[i]["time"] = times[i]
            legs[i]["quantity"] = quantities[i]
            legs[i]["price"] = prices[i]
            legs[i]["fee"] = fees[i]
        return legs


# Helper functions

def _create_equity_curve_figure(df: pd.DataFrame, start_date: str, end_date: str):
    """Create the equity curve figure."""
    import plotly.graph_objs as go
    
    # Create a simple equity curve based on cumulative returns
    df_sorted = df.sort_values('date')
    df_sorted['cumulative_pnl'] = df_sorted['return_dollar'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['cumulative_pnl'],
        mode='lines',
        name='Equity Curve',
        line=dict(color='#00FFCC', width=2)
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        template="plotly_dark",
        plot_bgcolor="#23273A",
        paper_bgcolor="#23273A",
        font=dict(color="#F6F8FA"),
        xaxis=dict(showgrid=True, gridcolor="#3A3F4B"),
        yaxis=dict(showgrid=True, gridcolor="#3A3F4B"),
    )
    
    return fig


def _create_summary_stats(df: pd.DataFrame) -> List:
    """Create comprehensive summary statistics cards."""
    if df.empty:
        return [html.Div("No trades to summarize.")]
    
    # Calculate comprehensive stats
    total_trades = len(df)
    wins = len(df[df['status'] == 'WIN'])
    losses = len(df[df['status'] == 'LOSS'])
    open_trades = len(df[df['status'] == 'OPEN'])
    
    # Win rate calculation
    closed_trades = wins + losses
    win_rate = (wins / max(1, closed_trades)) * 100 if closed_trades > 0 else 0
    
    # P&L calculations
    total_pnl = df['return_dollar'].sum()
    avg_win = df[df['status'] == 'WIN']['return_dollar'].mean() if wins > 0 else 0
    avg_loss = df[df['status'] == 'LOSS']['return_dollar'].mean() if losses > 0 else 0
    
    # Create stat cards in a grid layout
    stats = [
        html.Div([
            html.Div([
                html.H4(f"{wins}", className="stat-value", style={"color": "#00FFCC"}),
                html.P("Wins", className="stat-label"),
            ], className="stat-card"),
            html.Div([
                html.H4(f"{losses}", className="stat-value", style={"color": "#FF4C6A"}),
                html.P("Losses", className="stat-label"),
            ], className="stat-card"),
            html.Div([
                html.H4(f"{open_trades}", className="stat-value", style={"color": "#FFA500"}),
                html.P("Open", className="stat-label"),
            ], className="stat-card"),
        ], className="stats-row"),
        html.Div([
            html.Div([
                html.H4(f"${avg_win:.2f}", className="stat-value", style={"color": "#00FFCC"}),
                html.P("Avg Win", className="stat-label"),
            ], className="stat-card"),
            html.Div([
                html.H4(f"${avg_loss:.2f}", className="stat-value", style={"color": "#FF4C6A"}),
                html.P("Avg Loss", className="stat-label"),
            ], className="stat-card"),
            html.Div([
                html.H4(f"${total_pnl:.2f}", className="stat-value", style={"color": "#FFFFFF"}),
                html.P("Total P&L", className="stat-label"),
            ], className="stat-card"),
        ], className="stats-row"),
    ]
    
    return stats


def _create_leg_row(index: int, leg: Dict[str, Any]):
    """Create a leg row for the legs table."""
    return dbc.Row([
        dbc.Col([
            dbc.Button(
                "✖", 
                id={"type": "remove-leg-btn", "index": index}, 
                color="danger", 
                size="md", 
                className="me-2", 
                style={
                    "padding": "0 10px", 
                    "fontSize": "1.3rem", 
                    "height": "38px", 
                    "width": "38px"
                }
            ),
            dbc.Select(
                id={"type": "leg-action", "index": index},
                options=[
                    {"label": "BUY", "value": "BUY"},
                    {"label": "SELL", "value": "SELL"},
                ],
                value=leg.get("action", "BUY"),
                style={"width": "100px", "display": "inline-block", "marginLeft": "8px"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": "leg-date", "index": index},
                type="date",
                value=leg.get("date", date.today().isoformat()),
                style={"width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": "leg-time", "index": index},
                type="time",
                value=leg.get("time", "09:30"),
                style={"width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": "leg-quantity", "index": index},
                type="number",
                value=leg.get("quantity", 1),
                min=1,
                style={"width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": "leg-price", "index": index},
                type="number",
                value=leg.get("price", 1.0),
                min=0,
                step=0.01,
                style={"width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": "leg-fee", "index": index},
                type="number",
                value=leg.get("fee", 0.0),
                min=0,
                step=0.01,
                style={"width": "100%"}
            ),
        ], width=2),
    ], className="mb-2")


# Utility functions for trade management

def get_user_id(username: str) -> int:
    """Get user ID from username."""
    users = db_access.get_all_users()
    for user in users:
        if user["username"] == username:
            return user["id"]
    return 1  # Default fallback


def get_asset_type(symbol: str) -> str:
    """Determine asset type from symbol."""
    if len(symbol) <= 5 and symbol.isalpha():
        return "stock"
    elif "USDT" in symbol or "BTC" in symbol:
        return "crypto"
    else:
        return "other"
