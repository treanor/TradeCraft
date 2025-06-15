"""
Trade Craft Dash App Entry Point

- Multi-page support using dash.page_registry
- Main layout: title bar, navigation, persistent filter sidebar, and page container
"""
import dash
from dash import html, dcc
from components.filters import filter_header
from config import APP_TITLE, LOGO_PATH, is_debug_mode

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title=APP_TITLE
)

# Main layout: title bar, nav, filters, and page content
app.layout = html.Div([
    html.Div([
        html.Img(src=LOGO_PATH, height="60px", style={"marginRight": "20px"}),
        html.H1(APP_TITLE, style={"display": "inline-block", "verticalAlign": "middle", "margin": 0}),
    ], style={"display": "flex", "alignItems": "center", "padding": "10px 20px", "background": "#222", "color": "#fff"}),
    html.Nav([
        html.A("Trade Log", href="/trade_log", style={"marginRight": "20px", "color": "#fff"}),
        html.A("Analytics", href="/analytics", style={"marginRight": "20px", "color": "#fff"}),
        html.A("Calendar", href="/calendar", style={"color": "#fff"}),
    ], style={"padding": "10px 20px", "background": "#343a40"}),
    html.Div([
        html.Div([
            html.H5("Filters", style={"marginTop": "10px"}),
            filter_header(),
        ], style={"width": "350px", "padding": "20px", "background": "#f8f9fa", "borderRight": "1px solid #ddd", "minHeight": "80vh"}),
        html.Div(
            dash.page_container,
            style={"flex": 1, "padding": "30px"},
        ),
    ], style={"display": "flex"}),    dcc.Store(id="filtered-trades-store"),
    dcc.Store(id="user-store", storage_type="local", data=3),  # Default to alice (user_id=3)
])

# Central callback: update filtered-trades-store when any filter changes
from dash.dependencies import Input, Output, State
from utils.view_models.trade_log_view_model import TradeLogViewModel
from utils import db_access
from config import get_default_user

# Initialize ViewModel
trade_log_vm = TradeLogViewModel()
@app.callback(
    Output("filtered-trades-store", "data"),
    [
        Input("account-dropdown", "value"),
        Input("date-filter", "start_date"),
        Input("date-filter", "end_date"),
        Input("tag-filter", "value"),
        Input("symbol-filter", "value"),
    ]
)
def update_filtered_trades_store(
    account_id: int,
    start_date: str,
    end_date: str,
    tags: list[str],
    symbols: list[str],
) -> str:
    """
    Fetch and filter trades based on user-selected filters, and store as JSON for all subpages.
    This is the central data pipeline - ViewModel handles the filtering logic.
    """
    return trade_log_vm.get_filtered_trades_data(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,        tags=tags,
        symbols=symbols
    )

if __name__ == "__main__":
    app.run_server(debug=is_debug_mode())
