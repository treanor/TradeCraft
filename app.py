import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
from models import Trade, TradeLeg
from sample_data import sample_trades
from layout import stats_page_layout, calendar_page_layout, filter_buttons_row
from stats_utils import get_wins, get_losses, get_total_pnl, filter_trades, get_equity_curve

def create_app():
    app = dash.Dash(__name__, title="TradeCraft Journal", suppress_callback_exceptions=True)

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="active-filter", data="all"),
        html.Div([
            html.Div("TradeCraft Journal", className="sidebar-title"),
            html.Div([
                html.Div("$788.00", className="sidebar-balance"),
                html.Div("Cash: -$1,185.00", className="sidebar-cash"),
                html.Div("Active: $1,973.00", className="sidebar-active"),
            ], className="sidebar-balance-block"),
            html.Div([
                html.Button("New Trade", className="sidebar-btn primary"),
                html.Button("New Setup", className="sidebar-btn secondary"),
                html.Button("New Note", className="sidebar-btn note"),
            ], className="sidebar-btn-block"),
            html.Ul([
                html.Li(dcc.Link("Dashboard", href="/", style={"color": "inherit", "textDecoration": "none"})),
                html.Li(dcc.Link("Stats", href="/stats", style={"color": "inherit", "textDecoration": "none"})),
                html.Li(dcc.Link("Calendar", href="/calendar", style={"color": "inherit", "textDecoration": "none"})),
                html.Li("Settings"),
                html.Li("Help"),
            ], className="sidebar-menu"),
        ], className="sidebar"),
        html.Div(id="page-content", className="main-content"),
    ], className="app-container")

    app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>TradeCraft Journal</title>
        {%favicon%}
        {%css%}
        <style>
            body { background: #181e2a; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; }
            .app-container { display: flex; height: 100vh; }
            .sidebar { width: 240px; background: #1a2236; padding: 24px 12px; display: flex; flex-direction: column; }
            .sidebar-title { font-size: 1.6em; font-weight: bold; margin-bottom: 32px; }
            .sidebar-balance-block { margin-bottom: 32px; }
            .sidebar-balance { font-size: 1.4em; font-weight: bold; color: #4fc3f7; }
            .sidebar-cash, .sidebar-active { font-size: 0.95em; color: #b0bec5; }
            .sidebar-btn-block { display: flex; flex-direction: column; gap: 10px; margin-bottom: 32px; }
            .sidebar-btn { padding: 10px 0; border: none; border-radius: 6px; font-size: 1em; cursor: pointer; }
            .sidebar-btn.primary { background: #4fc3f7; color: #181e2a; font-weight: bold; }
            .sidebar-btn.secondary { background: #232b3e; color: #fff; }
            .sidebar-btn.note { background: #ffe082; color: #181e2a; }
            .sidebar-menu { list-style: none; padding: 0; margin: 0; }
            .sidebar-menu li { padding: 10px 0; color: #b0bec5; cursor: pointer; }
            .sidebar-menu li:hover { color: #4fc3f7; }
            .main-content { flex: 1; padding: 32px 40px; overflow-y: auto; }
            .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
            .topbar-btns button { background: #232b3e; color: #fff; border: none; border-radius: 6px; margin-right: 8px; padding: 8px 16px; font-size: 1em; cursor: pointer; }
            .topbar-btns button:hover { background: #4fc3f7; color: #181e2a; }
            .topbar-user { background: #232b3e; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; }
            .chart-stats-block { display: flex; align-items: flex-start; gap: 32px; margin-bottom: 32px; }
            .stats-row { display: flex; gap: 32px; align-items: center; }
            .stat-block { background: #232b3e; border-radius: 8px; padding: 16px 24px; min-width: 100px; text-align: center; }
            .stat-label { font-size: 0.95em; color: #b0bec5; margin-bottom: 4px; }
            .stat-value { font-size: 1.3em; font-weight: bold; }
            .stat-value.win { color: #4caf50; }
            .stat-value.loss { color: #f44336; }
            .stat-value.pnl { color: #4fc3f7; }
            .trades-table-block { background: #232b3e; border-radius: 10px; padding: 24px; }
            .dash-table-container .dash-spreadsheet-container { background: #232b3e !important; }
            .calendar-nav-btn { background: #4fc3f7; color: #181e2a; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; }
            .calendar-month-label { font-size: 1.2em; font-weight: bold; margin: 0 16px; color: #fff; }
            .calendar-days-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
            .calendar-day-label { flex: 1; text-align: center; font-size: 0.9em; color: #b0bec5; }
            .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
            .calendar-day-cell { background: #232b3e; border-radius: 6px; padding: 8px 0; }
            .calendar-day-number { font-size: 1.1em; }
            .calendar-weekly-summary { margin-top: 16px; font-size: 0.9em; color: #b0bec5; }
            .filter-btns-container { margin-bottom: 16px; }
            .filter-btns-row { marginBottom: 18px; display: flex; gap: 12px; }
            .filter-btn { border: none; border-radius: 20px; padding: 10px 24px; font-size: 1em; font-weight: bold; background: #232b3e; color: #b0bec5; cursor: pointer; transition: background 0.2s, color 0.2s; }
            .filter-btn.active, .filter-btn:hover { background: #4fc3f7; color: #181e2a; }
            .filter-btn.reset-btn { background: #ffe082; color: #181e2a; font-weight: bold; }
            .filter-btn.reset-btn.disabled, .filter-btn.reset-btn:disabled { background: #232b3e; color: #b0bec5; cursor: not-allowed; }
            /* --- Improved stats panel styles --- */
            .stats-section-header {
                font-size: 1.2em;
                font-weight: bold;
                color: #4fc3f7;
                margin-bottom: 12px;
                margin-top: 24px;
            }
            .stat-cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 18px;
                margin-bottom: 18px;
            }
            .stat-cards-row {
                display: flex;
                flex-wrap: wrap;
                gap: 18px;
                margin-bottom: 18px;
            }
            .stat-card {
                background: #232b3e;
                border-radius: 10px;
                padding: 18px 20px;
                min-width: 140px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            }
            .stat-card.small {
                padding: 12px 10px;
                min-width: 110px;
            }
            .stat-value.highlight {
                color: #4fc3f7;
                font-size: 1.5em;
            }
            .stats-section {
                margin-bottom: 12px;
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
"""

    from callbacks import register_callbacks
    register_callbacks(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
