from dash import html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd

def filter_buttons_row(active_filter):
    FILTER_OPTIONS = [
        ("All", "all"),
        ("Today", "today"),
        ("Yesterday", "yesterday"),
        ("This wk.", "this_week"),
        ("Last wk.", "last_week"),
        ("This mo.", "this_month"),
    ]
    return html.Div([
        html.Button(
            label,
            id={"type": "filter-btn", "value": value},
            n_clicks=0,
            className=f"filter-btn{' active' if value == active_filter else ''}"
        ) for label, value in FILTER_OPTIONS
    ], className="filter-btns-row", style={"marginBottom": "18px", "display": "flex", "gap": "12px"})

def filter_bar(active_filter, all_tags, selected_tags=None):
    if selected_tags is None:
        selected_tags = []
    return html.Div([
        filter_buttons_row(active_filter),
        dcc.Dropdown(
            id="tag-filter-dropdown",
            options=[{"label": tag, "value": tag} for tag in sorted(all_tags) if tag != "--NO TAGS--"] + [{"label": "--NO TAGS--", "value": "--NO TAGS--"}],
            value=selected_tags,
            multi=True,
            placeholder="Filter by tag(s)...",
            style={"width": "320px", "marginLeft": "18px"}
        )
    ], style={"display": "flex", "alignItems": "center", "gap": "12px", "marginBottom": "18px"})

# --- Improved stats panel layout ---
def stats_page_layout():
    # Section: General Stats
    general_stats = html.Div([
        html.Div("General Stats", className="stats-section-header"),
        html.Div([
            html.Div([
                html.Div("WIN RATE", className="stat-label"),
                html.Div("52%", className="stat-value highlight"),
            ], className="stat-card"),
            html.Div([
                html.Div("EXPECTANCY", className="stat-label"),
                html.Div("16", className="stat-value"),
            ], className="stat-card"),
            html.Div([
                html.Div("PROFIT FACTOR", className="stat-label"),
                html.Div("1.36", className="stat-value highlight"),
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
        ], className="stat-cards-grid"),
    ], className="stats-section")

    # Section: Streaks & Top Trades
    streaks_top = html.Div([
        html.Div("Streaks & Top Trades", className="stats-section-header"),
        html.Div([
            html.Div([
                html.Div("WIN STREAK", className="stat-label"),
                html.Div("5", className="stat-value win"),
            ], className="stat-card small"),
            html.Div([
                html.Div("LOSS STREAK", className="stat-label"),
                html.Div("5", className="stat-value loss"),
            ], className="stat-card small"),
            html.Div([
                html.Div("TOP LOSS", className="stat-label"),
                html.Div("-$532.00 (-61.1%)", className="stat-value loss highlight"),
            ], className="stat-card small"),
            html.Div([
                html.Div("TOP WIN", className="stat-label"),
                html.Div("$770.00 (102.7%)", className="stat-value win highlight"),
            ], className="stat-card small"),
            html.Div([
                html.Div("AVG DAILY VOL", className="stat-label"),
                html.Div("13", className="stat-value"),
            ], className="stat-card small"),
            html.Div([
                html.Div("AVG SIZE", className="stat-label"),
                html.Div("5", className="stat-value"),
            ], className="stat-card small"),
        ], className="stat-cards-row"),
    ], className="stats-section")

    # Section: Equity Curve
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

    # Section: Performance Charts
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

    # Section: Tag and Symbol Tables
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
        general_stats,
        streaks_top,
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

def stats_page_layout_dynamic(trades, active_filter, selected_tags):
    from stats_utils import (
        get_wins, get_losses, get_total_pnl, get_equity_curve,
        get_expectancy, get_profit_factor, get_avg_win_hold, get_avg_loss_hold,
        get_avg_win, get_avg_loss, get_win_streak, get_loss_streak,
        get_top_win, get_top_loss, get_avg_daily_vol, get_avg_size,
        get_avg_win_pct, get_avg_loss_pct, get_top_win_pct, get_top_loss_pct,
        get_performance_by_day_of_week, get_performance_by_hour,
        get_stats_by_tag, get_stats_by_symbol
    )
    import plotly.graph_objs as go
    import pandas as pd
    from datetime import timedelta
    wins = get_wins(trades)
    losses = get_losses(trades)
    pnl = get_total_pnl(trades)
    pnl_str = f"${pnl:,.2f}"
    win_rate = f"{(wins / (wins + losses) * 100):.0f}%" if (wins + losses) > 0 else "-"
    expectancy = get_expectancy(trades)
    expectancy_str = f"${expectancy:,.2f}" if expectancy or expectancy == 0 else "-"
    profit_factor = get_profit_factor(trades)
    profit_factor_str = f"{profit_factor:.2f}" if profit_factor != float('inf') else "∞"
    # Hold times
    avg_win_hold_sec = get_avg_win_hold(trades)
    avg_loss_hold_sec = get_avg_loss_hold(trades)
    def format_hold_sec(sec):
        if sec == 0:
            return "-"
        td = timedelta(seconds=sec)
        days = td.days
        hours = td.seconds // 3600
        mins = (td.seconds % 3600) // 60
        if days > 0:
            return f"{days} DAY{'S' if days != 1 else ''}"
        if hours > 0:
            return f"{hours} HR{'S' if hours != 1 else ''}"
        if mins > 0:
            return f"{mins} MIN"
        return "<1 MIN"
    avg_win_hold_str = format_hold_sec(avg_win_hold_sec)
    avg_loss_hold_str = format_hold_sec(avg_loss_hold_sec)
    # Avg win/loss $ and %
    avg_win = get_avg_win(trades)
    avg_win_pct = get_avg_win_pct(trades)
    avg_loss = get_avg_loss(trades)
    avg_loss_pct = get_avg_loss_pct(trades)
    avg_win_str = f"${avg_win:,.2f} ({avg_win_pct:.1f}%)" if (avg_win or avg_win == 0) else "-"
    avg_loss_str = f"${avg_loss:,.2f} ({avg_loss_pct:.1f}%)" if (avg_loss or avg_loss == 0) else "-"
    # Streaks
    win_streak = get_win_streak(trades)
    loss_streak = get_loss_streak(trades)
    # Top win/loss $ and %
    top_win = get_top_win(trades)
    top_win_pct = get_top_win_pct(trades)
    top_loss = get_top_loss(trades)
    top_loss_pct = get_top_loss_pct(trades)
    top_win_str = f"${top_win:,.2f} ({top_win_pct:.1f}%)" if (top_win or top_win == 0) else "-"
    top_loss_str = f"${top_loss:,.2f} ({top_loss_pct:.1f}%)" if (top_loss or top_loss == 0) else "-"
    # Avg daily vol, avg size
    avg_daily_vol = get_avg_daily_vol(trades)
    avg_size = get_avg_size(trades)
    # --- Performance by day of week ---
    perf_by_day_data = get_performance_by_day_of_week(trades)
    perf_by_day = dcc.Graph(
        figure={
            "data": [go.Bar(
                y=list(perf_by_day_data.keys()),
                x=list(perf_by_day_data.values()),
                orientation="h",
                marker_color=["#4caf50" if v >= 0 else "#f44336" for v in perf_by_day_data.values()],
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
    # --- Performance by hour ---
    perf_by_hour_data = get_performance_by_hour(trades)
    perf_by_hour = dcc.Graph(
        figure={
            "data": [go.Bar(
                y=list(perf_by_hour_data.keys()),
                x=list(perf_by_hour_data.values()),
                orientation="h",
                marker_color=["#4caf50" if v >= 0 else "#f44336" for v in perf_by_hour_data.values()],
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
    # --- Tag and Symbol tables ---
    tag_table = dash_table.DataTable(
        columns=[
            {"name": "Tag", "id": "Tag"},
            {"name": "Trades", "id": "Trades"},
            {"name": "PnL", "id": "PnL"},
            {"name": "PnL %", "id": "PnL %"},
            {"name": "Weighted %", "id": "Weighted %"},
        ],
        data=get_stats_by_tag(trades),
        style_header={"backgroundColor": "#232b3e", "color": "#fff", "fontWeight": "bold"},
        style_cell={"backgroundColor": "#181e2a", "color": "#fff", "border": "none", "padding": "8px"},
        style_table={"backgroundColor": "#181e2a", "marginTop": "10px"},
    )
    symbol_table = dash_table.DataTable(
        columns=[
            {"name": "Symbol", "id": "Symbol"},
            {"name": "Trades", "id": "Trades"},
            {"name": "PnL", "id": "PnL"},
            {"name": "PnL %", "id": "PnL %"},
            {"name": "Weighted %", "id": "Weighted %"},
        ],
        data=get_stats_by_symbol(trades),
        style_header={"backgroundColor": "#232b3e", "color": "#fff", "fontWeight": "bold"},
        style_cell={"backgroundColor": "#181e2a", "color": "#fff", "border": "none", "padding": "8px"},
        style_table={"backgroundColor": "#181e2a", "marginTop": "10px"},
    )
    # --- Equity curve and layout ---
    x_curve, y_curve = get_equity_curve(trades, active_filter)
    equity_curve = dcc.Graph(
        figure={
            "data": [go.Scatter(
                x=x_curve,
                y=y_curve,
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
    # --- General stats section
    general_stats = html.Div([
        html.Div("General Stats", className="stats-section-header"),
        html.Div([
            html.Div([
                html.Div("WIN RATE", className="stat-label"),
                html.Div(win_rate, className="stat-value highlight"),
            ], className="stat-card"),
            html.Div([
                html.Div("EXPECTANCY", className="stat-label"),
                html.Div(expectancy_str, className="stat-value"),
            ], className="stat-card"),
            html.Div([
                html.Div("PROFIT FACTOR", className="stat-label"),
                html.Div(profit_factor_str, className="stat-value highlight"),
            ], className="stat-card"),
            html.Div([
                html.Div("AVG WIN HOLD", className="stat-label"),
                html.Div(avg_win_hold_str, className="stat-value"),
            ], className="stat-card"),
            html.Div([
                html.Div("AVG LOSS HOLD", className="stat-label"),
                html.Div(avg_loss_hold_str, className="stat-value"),
            ], className="stat-card"),
            html.Div([
                html.Div("AVG LOSS", className="stat-label"),
                html.Div(avg_loss_str, className="stat-value loss"),
            ], className="stat-card"),
            html.Div([
                html.Div("AVG WIN", className="stat-label"),
                html.Div(avg_win_str, className="stat-value win"),
            ], className="stat-card"),
        ], className="stat-cards-grid"),
    ], className="stats-section")
    # Streaks & Top Trades
    streaks_top = html.Div([
        html.Div("Streaks & Top Trades", className="stats-section-header"),
        html.Div([
            html.Div([
                html.Div("WIN STREAK", className="stat-label"),
                html.Div(str(win_streak), className="stat-value win"),
            ], className="stat-card small"),
            html.Div([
                html.Div("LOSS STREAK", className="stat-label"),
                html.Div(str(loss_streak), className="stat-value loss"),
            ], className="stat-card small"),
            html.Div([
                html.Div("TOP LOSS", className="stat-label"),
                html.Div(top_loss_str, className="stat-value loss highlight"),
            ], className="stat-card small"),
            html.Div([
                html.Div("TOP WIN", className="stat-label"),
                html.Div(top_win_str, className="stat-value win highlight"),
            ], className="stat-card small"),
            html.Div([
                html.Div("AVG DAILY VOL", className="stat-label"),
                html.Div(f"{avg_daily_vol:.2f}", className="stat-value"),
            ], className="stat-card small"),
            html.Div([
                html.Div("AVG SIZE", className="stat-label"),
                html.Div(f"{avg_size:.2f}", className="stat-value"),
            ], className="stat-card small"),
        ], className="stat-cards-row"),
    ], className="stats-section")

    all_tags = set(tag for t in trades for tag in getattr(t, "tags", []) if tag)
    filterbar = filter_bar(active_filter, all_tags, selected_tags)

    # --- Layout with filter bar ---
    return html.Div([
        filterbar,
        general_stats,
        streaks_top,
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
