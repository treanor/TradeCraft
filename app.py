"""
Trade Craft Dash App Entry Point

Enhanced with better error handling, configuration, and logging.
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import logging
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.append(str(Path(__file__).parent))

from utils.config import config
from utils.db_init import initialize_database

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.is_development else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    initialize_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    sys.exit(1)

# Create Dash app with enhanced configuration
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title=config.app.title,
    update_title="Loading...",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Professional trading journal and analytics platform"}
    ]
)

# Enhanced navigation bar with better styling
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link(
            [html.I(className="fas fa-chart-line me-2"), "Trade Log"], 
            href="/trade_log", 
            className="nav-link text-light"
        )),
        dbc.NavItem(dcc.Link(
            [html.I(className="fas fa-analytics me-2"), "Analytics"], 
            href="/analytics", 
            className="nav-link text-light"
        )),
        dbc.NavItem(dcc.Link(
            [html.I(className="fas fa-calendar me-2"), "Calendar"], 
            href="/calendar", 
            className="nav-link text-light"
        )),
        dbc.NavItem(dcc.Link(
            [html.I(className="fas fa-cog me-2"), "Settings"], 
            href="/settings", 
            className="nav-link text-light"
        )),
    ],
    brand=[
        html.I(className="fas fa-chart-bar me-2"),
        config.app.title
    ],
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4 shadow-sm",
    style={"borderBottom": "3px solid #0056b3"}
)

# Enhanced app layout with error boundary
app.layout = dbc.Container([
    dcc.Location(id="url-redirector", refresh=True),
    navbar,
    dcc.Store(id="app-error-store"),
    html.Div(id="error-display"),
    dash.page_container
], fluid=True, className="px-0")

# Enhanced redirect callback with error handling
@app.callback(
    dash.dependencies.Output("url-redirector", "pathname"),
    dash.dependencies.Input("url-redirector", "pathname"),
    prevent_initial_call=True
)
def redirect_root(pathname):
    """Redirect from root to trade log page."""
    try:
        if pathname == "/":
            logger.info("Redirecting from root to trade log")
            return "/trade_log"
        return dash.no_update
    except Exception as e:
        logger.error(f"Error in redirect callback: {e}")
        return dash.no_update

# Global error handler
@app.callback(
    dash.dependencies.Output("error-display", "children"),
    dash.dependencies.Input("app-error-store", "data"),
    prevent_initial_call=True
)
def display_error(error_data):
    """Display global application errors."""
    if error_data:
        return dbc.Alert(
            [
                html.H4("Application Error", className="alert-heading"),
                html.P(error_data.get("message", "An unexpected error occurred")),
                html.Hr(),
                html.P("Please refresh the page or contact support if the problem persists.", 
                       className="mb-0")
            ],
            color="danger",
            dismissable=True
        )
    return ""

# Custom CSS for enhanced styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .nav-link:hover {
                background-color: rgba(255,255,255,0.1) !important;
                border-radius: 4px;
            }
            .card {
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border: none;
            }
            .btn {
                border-radius: 6px;
            }
            .table {
                border-radius: 8px;
                overflow: hidden;
            }
            .loading-spinner {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 200px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == "__main__":
    try:
        logger.info(f"Starting Trade Craft on {config.app.host}:{config.app.port}")
        app.run_server(
            debug=config.app.debug,
            host=config.app.host,
            port=config.app.port,
            dev_tools_hot_reload=config.is_development,
            dev_tools_ui=config.is_development
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)