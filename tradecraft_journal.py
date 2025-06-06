import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
from models import Trade, TradeLeg
from datetime import datetime
from sample_data import sample_trades

# Convert sample_trades to DataFrame
df = pd.DataFrame([t.to_dashboard_row() for t in sample_trades])

def get_equity_curve(trades, filter_key="all"):
    # Only include closed trades (WIN/LOSS)
    closed_trades = [t for t in trades if t.status.upper() in ("WIN", "LOSS") and len(t.legs) > 1]
    from collections import defaultdict
    import pandas as pd
    pnl_by_date = defaultdict(float)
    if filter_key in ("today", "yesterday"):
        # Group by hour
        for t in closed_trades:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            close_dt = exit.datetime.replace(minute=0, second=0, microsecond=0)
            pnl_by_date[close_dt] += pnl
        if not pnl_by_date:
            return [], []
        # Get full hourly range for the day
        all_hours = pd.date_range(min(pnl_by_date.keys()), max(pnl_by_date.keys()), freq='H')
        x = []
        y = []
        equity = 0
        for h in all_hours:
            equity += pnl_by_date.get(h.to_pydatetime(), 0)
            x.append(h.strftime("%m/%d/%Y %H:00"))
            y.append(equity)
        return x, y
    else:
        # Group by trading day (Mon-Fri)
        for t in closed_trades:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            close_date = exit.datetime.date()
            pnl_by_date[close_date] += pnl
        if not pnl_by_date:
            return [], []
        all_dates = pd.date_range(min(pnl_by_date.keys()), max(pnl_by_date.keys()), freq='B')
        x = []
        y = []
        equity = 0
        for d in all_dates:
            d_date = d.date()
            equity += pnl_by_date.get(d_date, 0)
            x.append(d_date.strftime("%m/%d/%Y"))
            y.append(equity)
        return x, y

# Sample data for the line chart
x_curve, y_curve = get_equity_curve(sample_trades)
chart_data = go.Scatter(
    x=x_curve,
    y=y_curve,
    mode="lines+markers",
    line=dict(color="#4fc3f7", width=3),
    marker=dict(size=8)
)

app = dash.Dash(__name__, title="TradeCraft Journal", suppress_callback_exceptions=True)

# --- Helper functions for stats ---
def get_wins(trades):
    return sum(1 for t in trades if t.status == "WIN")

def get_losses(trades):
    return sum(1 for t in trades if t.status == "LOSS")

def get_total_pnl(trades):
    pnl = 0
    for t in trades:
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl += (exit.price - entry.price) * entry.quantity
    return pnl

def stats_page_layout():
    # Stat cards (top row)
    stat_cards = html.Div([
        html.Div([
            html.Div("WIN RATE", className="stat-label"),
            html.Div("52%", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("EXPECTANCY", className="stat-label"),
            html.Div("16", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("PROFIT FACTOR", className="stat-label"),
            html.Div("1.36", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG WIN HOLD", className="stat-label"),
            html.Div("4.4 DAYS", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG LOSS HOLD", className="stat-label"),
            html.Div("8.4 HRS", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG LOSS", className="stat-label"),
            html.Div("-$94.09 (-18.6%)", className="stat-value loss"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG WIN", className="stat-label"),
            html.Div("$118.08 (24.4%)", className="stat-value win"),
        ], className="stat-card"),
    ], className="stat-cards-row")

    # Streaks and top stats (second row)
    streak_cards = html.Div([
        html.Div([
            html.Div("WIN STREAK", className="stat-label"),
            html.Div("5", className="stat-value win"),
        ], className="stat-card"),
        html.Div([
            html.Div("LOSS STREAK", className="stat-label"),
            html.Div("5", className="stat-value loss"),
        ], className="stat-card"),
        html.Div([
            html.Div("TOP LOSS", className="stat-label"),
            html.Div("-$532.00 (-61.1%)", className="stat-value loss"),
        ], className="stat-card"),
        html.Div([
            html.Div("TOP WIN", className="stat-label"),
            html.Div("$770.00 (102.7%)", className="stat-value win"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG DAILY VOL", className="stat-label"),
            html.Div("13", className="stat-value"),
        ], className="stat-card"),
        html.Div([
            html.Div("AVG SIZE", className="stat-label"),
            html.Div("5", className="stat-value"),
        ], className="stat-card"),
    ], className="stat-cards-row")

    # Equity curve (line chart)
    equity_curve = dcc.Graph(
        figure={
            "data": [go.Scatter(
                x=["Jun 12, 24", "Jun 13, 24", "Jun 20, 24", "Jun 27, 24", "Jul 1, 24", "Jul 8, 24", "Jul 15, 24"],
                y=[400, 1400, 1200, 800, 900, 1200, 1400],
                mode="lines",
                line=dict(color="#4fc3f7", width=3),
                fill="tozeroy",
                fillcolor="rgba(79,195,247,0.08)",
            )],
            "layout": go.Layout(
                title="Equity Curve",
                paper_bgcolor="#181e2a",
                plot_bgcolor="#181e2a",
                font=dict(color="#fff"),
                margin=dict(l=30, r=30, t=40, b=30),
                height=220,
            )
        },
        config={"displayModeBar": False},
        style={"width": "100%"}
    )

    # Performance by day of week (bar chart)
    perf_by_day = dcc.Graph(
        figure={
            "data": [go.Bar(
                y=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                x=[100, 0, 0, 500, 0, 20, 0],
                orientation="h",
                marker_color=["#4caf50" if v >= 0 else "#f44336" for v in [100, 0, 0, 500, 0, 20, 0]],
            )],
            "layout": go.Layout(
                title="Performance by Day of Week",
                paper_bgcolor="#181e2a",
                plot_bgcolor="#181e2a",
                font=dict(color="#fff"),
                margin=dict(l=30, r=30, t=40, b=30),
                height=180,
            )
        },
        config={"displayModeBar": False},
        style={"width": "100%"}
    )

    # Performance by hour (bar chart)
    perf_by_hour = dcc.Graph(
        figure={
            "data": [go.Bar(
                y=["9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"],
                x=[100, 0, 0, 700, -200, 0, 0, 0, 0, 0],
                orientation="h",
                marker_color=["#4caf50" if v >= 0 else "#f44336" for v in [100, 0, 0, 700, -200, 0, 0, 0, 0, 0]],
            )],
            "layout": go.Layout(
                title="Performance by Hour",
                paper_bgcolor="#181e2a",
                plot_bgcolor="#181e2a",
                font=dict(color="#fff"),
                margin=dict(l=30, r=30, t=40, b=30),
                height=180,
            )
        },
        config={"displayModeBar": False},
        style={"width": "100%"}
    )

    # Tag table (left)
    tag_table = dash_table.DataTable(
        columns=[
            {"name": "Tag", "id": "Tag"},
            {"name": "Trades", "id": "Trades"},
            {"name": "PnL", "id": "PnL"},
            {"name": "PnL %", "id": "PnL %"},
            {"name": "Weighted %", "id": "Weighted %"},
        ],
        data=[
            {"Tag": "Fidelity", "Trades": 6, "PnL": "$354.00", "PnL %": "44.00%", "Weighted %": "26.98%"},
            {"Tag": "TastyTrade", "Trades": 4, "PnL": "$347.00", "PnL %": "0.06%", "Weighted %": "26.45%"},
            {"Tag": "qqq", "Trades": 5, "PnL": "$316.00", "PnL %": "0.66%", "Weighted %": "24.09%"},
            {"Tag": "SPY", "Trades": 1, "PnL": "$208.00", "PnL %": "26.91%", "Weighted %": "15.85%"},
            {"Tag": "--NO TAGS--", "Trades": 40, "PnL": "$87.00", "PnL %": "102.67%", "Weighted %": "6.63%"},
        ],
        style_header={"backgroundColor": "#232b3e", "color": "#fff", "fontWeight": "bold"},
        style_cell={"backgroundColor": "#181e2a", "color": "#fff", "border": "none", "padding": "8px"},
        style_table={"backgroundColor": "#181e2a", "marginTop": "10px"},
    )

    # Symbol table (right)
    symbol_table = dash_table.DataTable(
        columns=[
            {"name": "Symbol", "id": "Symbol"},
            {"name": "Trades", "id": "Trades"},
            {"name": "PnL", "id": "PnL"},
            {"name": "PnL %", "id": "PnL %"},
            {"name": "Weighted %", "id": "Weighted %"},
        ],
        data=[
            {"Symbol": "NVDA240621C137", "Trades": 1, "PnL": "$770.00", "PnL %": "102.67%", "Weighted %": "97.72%"},
            {"Symbol": "NVDA240627C123", "Trades": 1, "PnL": "$249.00", "PnL %": "45.7%", "Weighted %": "31.60%"},
            {"Symbol": "NVDA240628C485", "Trades": 1, "PnL": "$242.00", "PnL %": "44.00%", "Weighted %": "30.71%"},
            {"Symbol": "SPY240816C560", "Trades": 1, "PnL": "$200.00", "PnL %": "26.91%", "Weighted %": "25.48%"},
            {"Symbol": "QQQ--240705P00432000", "Trades": 1, "PnL": "$200.00", "PnL %": "24.10%", "Weighted %": "23.48%"},
            {"Symbol": "QQQ240816C505", "Trades": 1, "PnL": "$156.00", "PnL %": "26.44%", "Weighted %": "19.80%"},
            {"Symbol": "QQQ240816C474", "Trades": 1, "PnL": "$145.00", "PnL %": "21.26%", "Weighted %": "17.14%"},
            {"Symbol": "QQQ--240710C00482000", "Trades": 1, "PnL": "$135.00", "PnL %": "21.26%", "Weighted %": "17.14%"},
            {"Symbol": "QQQ--240710C00482000", "Trades": 1, "PnL": "$130.00", "PnL %": "24.29%", "Weighted %": "16.93%"},
            {"Symbol": "QQQ--240710C00482000", "Trades": 1, "PnL": "$99.00", "PnL %": "10.65%", "Weighted %": "12.16%"},
            {"Symbol": "SPY240816C562", "Trades": 1, "PnL": "$59.00", "PnL %": "10.65%", "Weighted %": "9.16%"},
            {"Symbol": "BAC240816C41", "Trades": 1, "PnL": "$62.00", "PnL %": "19.50%", "Weighted %": "7.87%"},
        ],
        style_header={"backgroundColor": "#232b3e", "color": "#fff", "fontWeight": "bold"},
        style_cell={"backgroundColor": "#181e2a", "color": "#fff", "border": "none", "padding": "8px"},
        style_table={"backgroundColor": "#181e2a", "marginTop": "10px"},
    )

    return html.Div([
        stat_cards,
        streak_cards,
        html.Div([
            equity_curve
        ], style={"marginBottom": "16px"}),
        html.Div([
            html.Div(perf_by_day, style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
            html.Div(perf_by_hour, style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
        ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "marginBottom": "16px"}),
        html.Div([
            html.Div(tag_table, style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
            html.Div(symbol_table, style={"width": "49%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
        ], style={"width": "100%", "display": "flex", "justifyContent": "space-between"}),
    ], className="stats-main-content")

def calendar_page_layout():
    import calendar
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = now.month
    month_name = now.strftime('%B %Y')
    cal = calendar.Calendar()
    month_days = list(cal.itermonthdays(year, month))
    # Pad to 6 weeks (42 days)
    while len(month_days) < 42:
        month_days.append(0)
    weeks = [month_days[i:i+7] for i in range(0, 42, 7)]
    return html.Div([
        html.Div([
            html.Div([
                html.Button('<', className='calendar-nav-btn'),
                html.Div(month_name, className='calendar-month-label'),
                html.Button('>', className='calendar-nav-btn'),
            ], className='calendar-header', style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '16px', 'marginBottom': '16px'}),
            html.Div([
                html.Div(day, className='calendar-day-label') for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            ], className='calendar-days-row', style={'display': 'grid', 'gridTemplateColumns': 'repeat(7, 1fr)', 'marginBottom': '8px', 'fontWeight': 'bold', 'color': '#b0bec5'}),
            html.Div([
                html.Div([
                    html.Div(str(day) if day != 0 else '', className='calendar-day-number')
                ], className='calendar-day-cell', style={
                    'background': '#232b3e',
                    'borderRadius': '16px',
                    'height': '90px',
                    'margin': '4px',
                    'display': 'flex',
                    'alignItems': 'flex-start',
                    'justifyContent': 'flex-end',
                    'padding': '8px',
                    'color': '#b0bec5',
                    'fontWeight': 'bold',
                    'fontSize': '1.1em',
                }) for week in weeks for day in week
            ], className='calendar-grid', style={'display': 'grid', 'gridTemplateColumns': 'repeat(7, 1fr)', 'gap': '4px', 'marginBottom': '0'}),
        ], className='calendar-left', style={'flex': '1', 'minWidth': '650px', 'maxWidth': '900px'}),
        html.Div('Weekly Summary', className='calendar-weekly-summary', style={
            'background': '#232b3e',
            'borderRadius': '16px',
            'padding': '24px 12px',
            'color': '#b0bec5',
            'fontWeight': 'bold',
            'fontSize': '1.1em',
            'textAlign': 'center',
            'minWidth': '220px',
            'maxWidth': '260px',
            'marginLeft': '32px',
            'height': '100%',
            'alignSelf': 'flex-start',
        })
    ], className='calendar-main-content', style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'center',
        'alignItems': 'flex-start',
        'gap': '32px',
        'width': '100%',
        'maxWidth': '1300px',
        'margin': '0 auto',
        'padding': '24px 0 0 0',
        'boxSizing': 'border-box',
    })

# Filter options for dashboard filter buttons
FILTER_OPTIONS = [
    ("All", "all"),
    ("Today", "today"),
    ("Yesterday", "yesterday"),
    ("This wk.", "this_week"),
    ("Last wk.", "last_week"),
    ("This mo.", "this_month"),
]

def filter_trades(trades, filter_key):
    now = datetime.now()
    if filter_key == "all":
        return trades
    if filter_key == "today":
        return [t for t in trades if t.legs and t.legs[-1].datetime.date() == now.date()]
    elif filter_key == "yesterday":
        yest = now.date() - pd.Timedelta(days=1)
        return [t for t in trades if t.legs and t.legs[-1].datetime.date() == yest]
    elif filter_key == "this_week":
        start = now - pd.Timedelta(days=now.weekday())
        return [t for t in trades if t.legs and t.legs[-1].datetime.date() >= start.date()]
    elif filter_key == "last_week":
        start = now - pd.Timedelta(days=now.weekday() + 7)
        end = start + pd.Timedelta(days=6)
        return [t for t in trades if t.legs and start.date() <= t.legs[-1].datetime.date() <= end.date()]
    elif filter_key == "this_month":
        return [t for t in trades if t.legs and t.legs[-1].datetime.month == now.month and t.legs[-1].datetime.year == now.year]
    return trades

# Update default for dcc.Store
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

# --- Filter buttons row for dashboard ---
def filter_buttons_row(active_filter):
    return html.Div([
        html.Button(
            label,
            id={"type": "filter-btn", "value": value},
            n_clicks=0,
            className=f"filter-btn{' active' if value == active_filter else ''}"
        ) for label, value in FILTER_OPTIONS
    ], className="filter-btns-row", style={"marginBottom": "18px", "display": "flex", "gap": "12px"})

# --- Callback to update active filter ---
from dash import ctx, ALL

@app.callback(
    Output("active-filter", "data"),
    [Input({"type": "filter-btn", "value": ALL}, "n_clicks")],
    [State("active-filter", "data")],
    prevent_initial_call=True
)
def set_active_filter(n_clicks_list, current_filter):
    ctx_trigger = ctx.triggered_id
    if not n_clicks_list or all(n is None or n == 0 for n in n_clicks_list):
        return current_filter or "all"
    idx = n_clicks_list.index(max(n_clicks_list))
    return FILTER_OPTIONS[idx][1]

# --- Main dashboard/page callback ---
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname"), Input("active-filter", "data")],
)
def display_page(pathname, active_filter):
    if pathname == "/stats":
        return stats_page_layout()
    elif pathname == "/calendar":
        return calendar_page_layout()
    else:
        # Dashboard page
        trades = filter_trades(sample_trades, active_filter or "this_week")
        wins = sum(1 for t in trades if t.status.upper() == "WIN")
        losses = sum(1 for t in trades if t.status.upper() == "LOSS")
        pnl = get_total_pnl(trades)
        pnl_str = f"${pnl:,.2f}"
        x_curve, y_curve = get_equity_curve(trades, active_filter or "this_week")
        chart_data = go.Scatter(
            x=x_curve,
            y=y_curve,
            mode="lines+markers",
            line=dict(color="#4fc3f7", width=3),
            marker=dict(size=8)
        )
        return html.Div([
            filter_buttons_row(active_filter or "this_week"),
            html.Div([
                html.Div([None], className="topbar-btns"),
                html.Div("User", className="topbar-user"),
            ], className="topbar"),

            # Chart and stats
            html.Div([
                dcc.Graph(
                    id="pnl-chart",
                    figure={
                        "data": [chart_data],
                        "layout": go.Layout(
                            paper_bgcolor="#181e2a",
                            plot_bgcolor="#181e2a",
                            font=dict(color="#fff"),
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=150,
                        )
                    },
                    config={"displayModeBar": False},
                    style={"width": "100%"}
                ),
                html.Div([
                    html.Div([
                        html.Div("WINS", className="stat-label"),
                        html.Div(str(wins), className="stat-value win"),
                    ], className="stat-block"),
                    html.Div([
                        html.Div("LOSSES", className="stat-label"),
                        html.Div(str(losses), className="stat-value loss"),
                    ], className="stat-block"),
                    html.Div([
                        html.Div("PnL", className="stat-label"),
                        html.Div(pnl_str, className="stat-value pnl"),
                    ], className="stat-block"),
                ], className="stats-row"),
            ], className="chart-stats-block"),

            # Trades table
            html.Div([
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in pd.DataFrame([t.to_dashboard_row() for t in trades]).columns],
                    data=pd.DataFrame([t.to_dashboard_row() for t in trades]).to_dict("records"),
                    style_header={"backgroundColor": "#232b3e", "color": "#fff", "fontWeight": "bold"},
                    style_cell={"backgroundColor": "#181e2a", "color": "#fff", "border": "none", "padding": "8px"},
                    style_data_conditional=[
                        {"if": {"filter_query": '{Status} = "WIN"', "column_id": "Status"}, "color": "#4caf50"},
                        {"if": {"filter_query": '{Status} = "LOSS"', "column_id": "Status"}, "color": "#f44336"},
                        {"if": {"filter_query": '{Status} = "OPEN"', "column_id": "Status"}, "color": "#fff176"},
                    ],
                    style_table={"overflowX": "auto", "backgroundColor": "#181e2a"},
                )
            ], className="trades-table-block"),
        ])

# External CSS for dark theme and layout
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

if __name__ == "__main__":
    app.run(debug=True)
