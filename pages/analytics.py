"""
Analytics/Dashboard Page for Trade Craft
- Shows summary stats, P&L over time, win rate, asset allocation
"""
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from utils import db_access
import dash
from dash import dash_table
from datetime import datetime
from components.filters import filter_header, user_account_dropdowns
from utils.filters import apply_trade_filters

# Register this as a Dash page
# URL: /analytics

dash.register_page(__name__, path="/analytics", name="Analytics")

USERNAME = "alice"  # For now, single-user mode

def get_analytics_df(user_id: int, account_id: int) -> pd.DataFrame:
    """Fetch all trades for the selected user/account as a DataFrame with analytics columns."""
    trades = db_access.fetch_trades_for_user_and_account(user_id, account_id)
    if not trades:
        return pd.DataFrame()
    df = pd.DataFrame(trades)
    analytics = [db_access.trade_analytics(row["id"]) for _, row in df.iterrows()]
    df["realized_pnl"] = [a.get("realized_pnl", 0.0) for a in analytics]
    df["status"] = [a.get("status", "-") for a in analytics]
    # Robust datetime parsing for ISO8601 and mixed formats
    df["opened_at"] = pd.to_datetime(df["opened_at"], format="mixed", errors="coerce")
    df["asset_type"] = df["asset_type"].fillna("")
    # --- Add normalized 'symbol' column for filtering ---
    from utils import db_access as _db_access
    df["symbol"] = [", ".join(_db_access.get_symbols_for_trade(row["id"])) for _, row in df.iterrows()]
    return df

def summary_stats(df: pd.DataFrame) -> list:
    """Return summary stats as a styled neon/dark card."""
    if df.empty or "realized_pnl" not in df.columns:
        return [html.Div("No trades to summarize.")]
    total_trades = len(df)
    wins = (df["realized_pnl"] > 0).sum() if "realized_pnl" in df else 0
    losses = (df["realized_pnl"] < 0).sum() if "realized_pnl" in df else 0
    open_trades = (df["status"] == "open").sum() if "status" in df else 0
    win_rate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
    avg_win = df.loc[df["realized_pnl"] > 0, "realized_pnl"].mean() if "realized_pnl" in df and (df["realized_pnl"] > 0).any() else 0
    avg_loss = df.loc[df["realized_pnl"] < 0, "realized_pnl"].mean() if "realized_pnl" in df and (df["realized_pnl"] < 0).any() else 0
    total_pnl = df["realized_pnl"].sum() if "realized_pnl" in df else 0
    return [
        html.Div([
            html.Span("Total Trades", style={"color": "#b0dfff", "fontWeight": "bold"}),
            html.Span(f" {total_trades}", style={"color": "#fff", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Wins", style={"color": "#b0dfff", "fontWeight": "bold"}),
            html.Span(f" {wins}", style={"color": "#00FFCC", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Losses", style={"color": "#b0dfff", "fontWeight": "bold"}),
            html.Span(f" {losses}", style={"color": "#FF4C6A", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Open", style={"color": "#b0dfff", "fontWeight": "bold"}),
            html.Span(f" {open_trades}", style={"color": "#b0dfff", "fontWeight": "bold", "marginLeft": "8px"}),
        ], style={"fontSize": "1.1rem", "marginBottom": "8px"}),
        html.Div([
            html.Span("Win Rate", style={"color": "#b0dfff"}),
            html.Span(f" {win_rate:.1f}%", style={"color": "#00FFCC", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Avg Win", style={"color": "#b0dfff"}),
            html.Span(f" ${avg_win:.2f}", style={"color": "#00FFCC", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Avg Loss", style={"color": "#b0dfff"}),
            html.Span(f" ${avg_loss:.2f}", style={"color": "#FF4C6A", "fontWeight": "bold", "marginLeft": "8px"}),
            html.Span("  |  "),
            html.Span("Total P&L", style={"color": "#b0dfff"}),
            html.Span(f" ${total_pnl:.2f}", style={"color": "#00FFCC" if total_pnl >= 0 else "#FF4C6A", "fontWeight": "bold", "marginLeft": "8px"}),
        ], style={"fontSize": "1.1rem"}),
    ]

def pnl_over_time_figure(df: pd.DataFrame) -> go.Figure:
    """Return a Plotly figure of cumulative P&L over time (neon/dark theme)."""
    if df.empty:
        return go.Figure()
    df = df.sort_values("opened_at")
    df["cum_pnl"] = df["realized_pnl"].cumsum()
    fig = go.Figure(go.Scatter(
        x=df["opened_at"],
        y=df["cum_pnl"],
        mode="lines+markers",
        name="Equity Curve",
        line=dict(color="#1AA9E5", width=3),
        marker=dict(color="#00FFCC", size=8, line=dict(width=2, color="#181C25")),
        hoverlabel=dict(bgcolor="#23273A", font_size=14, font_family="Inter")
    ))
    fig.update_layout(
        title="Cumulative P&L Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative P&L",
        template="plotly_white",
        height=300,
        plot_bgcolor="#23273A",
        paper_bgcolor="#23273A",
        font=dict(color="#F6F8FA", family="Inter,Roboto,Montserrat,sans-serif"),
        xaxis=dict(color="#F6F8FA", gridcolor="#23273A"),
        yaxis=dict(color="#F6F8FA", gridcolor="#23273A"),
    )
    return fig

def asset_allocation_figure(df: pd.DataFrame) -> go.Figure:
    """Return a Plotly pie chart of asset allocation by asset_type (neon/dark theme)."""
    if df.empty:
        return go.Figure()
    asset_counts = df["asset_type"].value_counts()
    fig = go.Figure(go.Pie(
        labels=asset_counts.index,
        values=asset_counts.values,
        hole=0.4,
        marker=dict(colors=["#1AA9E5", "#00FFCC", "#23273A", "#b0dfff", "#FF4C6A"])
    ))
    fig.update_layout(
        title="Asset Allocation",
        height=300,
        paper_bgcolor="#23273A",
        font=dict(color="#F6F8FA", family="Inter,Roboto,Montserrat,sans-serif"),
        legend=dict(font=dict(color="#F6F8FA")),
    )
    return fig

def stat_card(title: str, value: str) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Div(title, className="small text-muted mb-1"),
            html.H4(value, className="mb-0")
        ])
    ], className="shadow-sm bg-dark text-light", style={"minWidth": 140, "marginRight": 12, "marginBottom": 12})

# Define tag_table and symbol_table before layout so they are available

def tag_table(df: pd.DataFrame) -> dash_table.DataTable:
    if df.empty or "id" not in df:
        return html.Div("No tag data.")
    import utils.db_access as db_access
    tag_rows = []
    for _, row in df.iterrows():
        tags = db_access.get_tags_for_trade(row["id"])
        if tags:
            for tag in tags:
                tag_rows.append({"tag": tag.strip(), "pnl": row["realized_pnl"]})
    tag_df = pd.DataFrame(tag_rows)
    if tag_df.empty:
        return html.Div("No tag data.")
    tag_stats = tag_df.groupby("tag").agg(trades=("pnl", "count"), pnl=("pnl", "sum")).reset_index()
    return dash_table.DataTable(
        columns=[{"name": "Tag", "id": "tag"}, {"name": "Trades", "id": "trades"}, {"name": "PnL", "id": "pnl"}],
        data=tag_stats.to_dict("records"),
        style_table={"overflowX": "auto", "background": "#23273A", "borderRadius": "16px"},
        style_cell={"background": "#23273A", "color": "#F6F8FA", "border": "none", "fontSize": "1.05rem"},
        style_header={"background": "#181C25", "color": "#00FFCC", "fontWeight": "bold", "borderBottom": "2px solid #00FFCC"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#222436"},
            {"if": {"column_id": "pnl", "filter_query": '{pnl} > 0'}, "color": "#00FFCC"},
            {"if": {"column_id": "pnl", "filter_query": '{pnl} < 0'}, "color": "#FF4C6A"},
        ],
        page_size=10
    )

def symbol_table(df: pd.DataFrame) -> dash_table.DataTable:
    if df.empty or "asset_symbol" not in df:
        return html.Div("No symbol data.")
    sym_stats = df.groupby("asset_symbol").agg(trades=("realized_pnl", "count"), pnl=("realized_pnl", "sum")).reset_index()
    return dash_table.DataTable(
        columns=[{"name": "Symbol", "id": "asset_symbol"}, {"name": "Trades", "id": "trades"}, {"name": "PnL", "id": "pnl"}],
        data=sym_stats.to_dict("records"),
        style_table={"overflowX": "auto", "background": "#23273A", "borderRadius": "16px"},
        style_cell={"background": "#23273A", "color": "#F6F8FA", "border": "none", "fontSize": "1.05rem"},
        style_header={"background": "#181C25", "color": "#00FFCC", "fontWeight": "bold", "borderBottom": "2px solid #00FFCC"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#222436"},
            {"if": {"column_id": "pnl", "filter_query": '{pnl} > 0'}, "color": "#00FFCC"},
            {"if": {"column_id": "pnl", "filter_query": '{pnl} < 0'}, "color": "#FF4C6A"},
        ],
        page_size=10
    )

# Get tag and symbol options from the data
analytics_df = get_analytics_df(user_id=None, account_id=None)  # Provide None to avoid KeyError if empty
if not analytics_df.empty and 'asset_symbol' in analytics_df.columns:
    tag_options = sorted({tag.strip() for tags in analytics_df.get('tags', []) if tags for tag in str(tags).split(',')})
    symbol_options = sorted(analytics_df['asset_symbol'].dropna().unique())
else:
    tag_options = []
    symbol_options = []

# In the main layout, add the dropdowns to the right of the Trade Craft header
# Modern Analytics Page Layout (neon/dark theme)
layout = html.Div([
    html.H2([
        html.Span("Analytics", className="section-title"),
        html.Span(" ", style={"marginLeft": "8px"}),
        html.Span("📊", style={"fontSize": "2rem", "verticalAlign": "middle"})
    ], style={"color": "#fff", "fontWeight": "bold", "marginBottom": "18px"}),
    html.Div(user_account_dropdowns(), style={"marginBottom": "18px"}),
    html.Div(filter_header(prefix="analytics", show_add_trade=False), className="filter-row", style={"marginBottom": "18px"}),
    html.Div([
        dcc.Graph(id="pnl-over-time", style={"background": "#23273A", "borderRadius": "16px", "boxShadow": "0 2px 16px #00FFCC33", "padding": "12px"}),
    ], className="card", style={"marginBottom": "24px"}),
    html.Div([
        html.Div(id="analytics-summary-stats", className="stats"),
    ], className="card", style={"marginBottom": "24px"}),
    html.Div([
        html.Div([
            html.H4("Asset Allocation", className="section-title", style={"fontSize": "1.3rem", "marginBottom": "12px"}),
            dcc.Graph(id="asset-allocation-chart", style={"background": "#23273A", "borderRadius": "16px", "boxShadow": "0 2px 16px #00FFCC33", "padding": "12px"}),
        ], className="card", style={"marginBottom": "24px"}),
        html.Div([
            html.H4("PnL by Tag", className="section-title", style={"fontSize": "1.3rem", "marginBottom": "12px"}),
            html.Div(id="tag-table-container"),
        ], className="card", style={"marginBottom": "24px"}),
        html.Div([
            html.H4("PnL by Symbol", className="section-title", style={"fontSize": "1.3rem", "marginBottom": "12px"}),
            html.Div(id="symbol-table-container"),
        ], className="card", style={"marginBottom": "24px"}),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "24px"}),
])

# Quick filter callback (sets date range based on which quickfilter button is pressed)
@callback(
    Output("analytics-date-filter", "start_date"),
    Output("analytics-date-filter", "end_date"),
    [
        Input("analytics-quickfilter-today", "n_clicks"),
        Input("analytics-quickfilter-yesterday", "n_clicks"),
        Input("analytics-quickfilter-thisweek", "n_clicks"),
        Input("analytics-quickfilter-lastweek", "n_clicks"),
        Input("analytics-quickfilter-thismonth", "n_clicks"),
        Input("analytics-quickfilter-lastmonth", "n_clicks"),
        Input("analytics-quickfilter-alltime", "n_clicks"),
        Input("analytics-clear-filters", "n_clicks"),
    ],
    prevent_initial_call=True
)
def set_analytics_quick_date_filter(today, yesterday, thisweek, lastweek, thismonth, lastmonth, alltime, clear):
    from dash import ctx
    triggered = ctx.triggered_id
    today_dt = pd.Timestamp.today().normalize()
    if triggered == "analytics-quickfilter-today":
        return today_dt.date().isoformat(), today_dt.date().isoformat()
    elif triggered == "analytics-quickfilter-yesterday":
        yest = today_dt - pd.Timedelta(days=1)
        return yest.date().isoformat(), yest.date().isoformat()
    elif triggered == "analytics-quickfilter-thisweek":
        start = today_dt - pd.Timedelta(days=today_dt.dayofweek)
        return start.date().isoformat(), today_dt.date().isoformat()
    elif triggered == "analytics-quickfilter-lastweek":
        start = today_dt - pd.Timedelta(days=today_dt.dayofweek + 7)
        end = start + pd.Timedelta(days=6)
        return start.date().isoformat(), end.date().isoformat()
    elif triggered == "analytics-quickfilter-thismonth":
        start = today_dt.replace(day=1)
        return start.date().isoformat(), today_dt.date().isoformat()
    elif triggered == "analytics-quickfilter-lastmonth":
        first_this_month = today_dt.replace(day=1)
        last_month_end = first_this_month - pd.Timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = last_month_end
        return start.date().isoformat(), end.date().isoformat()
    elif triggered == "analytics-quickfilter-alltime" or triggered == "analytics-clear-filters":
        return None, None
    return dash.no_update, dash.no_update

# Add a callback to reset all filter inputs when 'Clear Filters' is clicked
@callback(
    Output("analytics-symbol-filter", "value", allow_duplicate=True),
    Output("analytics-tag-filter", "value", allow_duplicate=True),
    Output("analytics-date-filter", "start_date", allow_duplicate=True),
    Output("analytics-date-filter", "end_date", allow_duplicate=True),
    Input("analytics-clear-filters", "n_clicks"),
    prevent_initial_call=True
)
def clear_analytics_filters(n_clicks: int):
    """Reset all analytics filter inputs when Clear Filters is clicked."""
    return None, None, None, None

# Main dashboard callback (update to use text input values for symbol/tag)
@callback(
    [
        Output("analytics-pnl-curve", "figure"),
        Output("analytics-perf-dow", "figure"),
        Output("analytics-perf-hour", "figure"),
        Output("stat-winrate", "children"),
        Output("stat-expectancy", "children"),
        Output("stat-profitfactor", "children"),
        Output("stat-avgwinhold", "children"),
        Output("stat-avglosshold", "children"),
        Output("stat-avgloss", "children"),
        Output("stat-avgwin", "children"),
        Output("stat-winstreak", "children"),
        Output("stat-lossstreak", "children"),
        Output("stat-topwin", "children"),
        Output("stat-toploss", "children"),
    ],
    [
        Input("analytics-date-filter", "start_date"),
        Input("analytics-date-filter", "end_date"),
        Input("analytics-tag-filter", "value"),
        Input("analytics-symbol-filter", "value"),
        Input("analytics-clear-filters", "n_clicks"),
        Input("user-store", "data"),
        Input("account-dropdown", "value"),
    ]
)
def update_dashboard(start_date, end_date, tag, symbol, n_clear, user_id, account_id):
    """Update analytics dashboard based on filters and selected user/account."""
    df = get_analytics_df(user_id, account_id)
    from dash import ctx
    if ctx.triggered_id == "analytics-clear-filters":
        start_date = end_date = tag = symbol = None
    tags = [t.strip() for t in tag.split(",") if t.strip()] if tag else []
    symbols = [s.strip() for s in symbol.split(",") if s.strip()] if symbol else []
    df = apply_trade_filters(df, start_date, end_date, tags, symbols)
    # Ensure 'realized_pnl' exists
    if "realized_pnl" not in df.columns:
        df["realized_pnl"] = 0.0
    if "status" not in df.columns:
        df["status"] = "-"
    total_trades = len(df)
    wins = (df["realized_pnl"] > 0).sum() if not df.empty else 0
    losses = (df["realized_pnl"] < 0).sum() if not df.empty else 0
    win_rate = f"{(wins / (wins + losses) * 100):.0f}%" if (wins + losses) > 0 else "-"
    expectancy = f"{(df['realized_pnl'].mean() if total_trades else 0):.2f}" if total_trades else "-"
    profit_factor = f"{(df[df['realized_pnl'] > 0]['realized_pnl'].sum() / abs(df[df['realized_pnl'] < 0]['realized_pnl'].sum())):.2f}" if losses > 0 else "-"
    # Calculate average win hold and loss hold
    avg_win_hold = "-"
    avg_loss_hold = "-"
    # Try to infer closed_at if not present
    if "closed_at" not in df.columns:
        # Try to get closed_at from trade analytics if available
        if "id" in df.columns:
            from utils import db_access
            closed_ats = []
            for trade_id in df["id"]:
                analytics = db_access.trade_analytics(trade_id)
                closed_ats.append(analytics.get("closed_at"))
            df["closed_at"] = pd.to_datetime(closed_ats, errors="coerce")
    if not df.empty and "opened_at" in df.columns and "closed_at" in df.columns:
        closed = df[df["status"] == "closed"].copy()
        closed["opened_at"] = pd.to_datetime(closed["opened_at"], errors="coerce")
        closed["closed_at"] = pd.to_datetime(closed["closed_at"], errors="coerce")
        closed = closed[closed["opened_at"].notnull() & closed["closed_at"].notnull()]
        if not closed.empty:
            closed["hold_time"] = closed["closed_at"] - closed["opened_at"]
            win_holds = closed.loc[closed["realized_pnl"] > 0, "hold_time"].dropna() if "realized_pnl" in closed else pd.Series()
            loss_holds = closed.loc[closed["realized_pnl"] < 0, "hold_time"].dropna() if "realized_pnl" in closed else pd.Series()
            if not win_holds.empty:
                avg_win_hold = str(win_holds.mean()).split(".")[0]
            if not loss_holds.empty:
                avg_loss_hold = str(loss_holds.mean()).split(".")[0]
    avg_loss = f"${df[df['realized_pnl'] < 0]['realized_pnl'].mean():.2f}" if losses > 0 else "-"
    avg_win = f"${df[df['realized_pnl'] > 0]['realized_pnl'].mean():.2f}" if wins > 0 else "-"
    win_streak = str(max_streak(df["realized_pnl"] > 0)) if total_trades else "-"
    loss_streak = str(max_streak(df["realized_pnl"] < 0)) if total_trades else "-"
    top_win = f"${df['realized_pnl'].max():.2f}" if not df.empty else "-"
    top_loss = f"${df['realized_pnl'].min():.2f}" if not df.empty else "-"
    pnl_curve = pnl_over_time_figure(df)
    perf_dow = performance_by_day_chart(df)
    perf_hour = performance_by_hour_chart(df)
    def card_val(val):
        return stat_card("", val)
    return (
        pnl_curve,
        perf_dow,
        perf_hour,
        card_val(win_rate),
        card_val(expectancy),
        card_val(profit_factor),
        card_val(avg_win_hold),
        card_val(avg_loss_hold),
        card_val(avg_loss),
        card_val(avg_win),
        card_val(win_streak),
        card_val(loss_streak),
        card_val(top_win),
        card_val(top_loss),
    )

def max_streak(series: pd.Series) -> int:
    streak = max_streak = 0
    for val in series:
        if val:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def performance_by_day_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    df["dow"] = df["opened_at"].dt.day_name()
    perf = df.groupby("dow")["realized_pnl"].sum().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ], fill_value=0)
    fig = go.Figure(go.Bar(x=perf.index, y=perf.values, marker_color=["#00d68f" if v >= 0 else "#ff3860" for v in perf.values]))
    fig.update_layout(title="Performance by Day of Week", template="plotly_dark", height=220, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def performance_by_hour_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    df["hour"] = df["opened_at"].dt.hour
    perf = df.groupby("hour")["realized_pnl"].sum().reindex(range(24), fill_value=0)
    fig = go.Figure(go.Bar(x=[f"{h}:00" for h in perf.index], y=perf.values, marker_color=["#00d68f" if v >= 0 else "#ff3860" for v in perf.values]))
    fig.update_layout(title="Performance by Hour", template="plotly_dark", height=220, margin=dict(l=0, r=0, t=30, b=0))
    return fig
