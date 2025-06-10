"""
Calendar Page for Trade Craft
Shows daily trade P&L and weekly summary in a calendar grid.
"""
from datetime import date, timedelta, datetime
import calendar
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from utils.db_access import fetch_trades_for_user
from components.filters import user_account_dropdowns
import utils.db_access as db_access

# Register page
dash.register_page(__name__, path="/calendar", name="Calendar")

USERNAME = "alice"

def get_trades_by_day(year: int, month: int, user_id: int, account_id: int) -> pd.DataFrame:
    trades = db_access.fetch_trades_for_user_and_account(user_id, account_id)
    df = pd.DataFrame(trades)
    if df.empty:
        return df
    df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    df = df[df["opened_at"].dt.year == year]
    df = df[df["opened_at"].dt.month == month]
    df["date"] = df["opened_at"].dt.date
    # --- Add realized_pnl column for calendar aggregation ---
    analytics = [db_access.trade_analytics(row["id"]) for _, row in df.iterrows()]
    df["realized_pnl"] = [a["realized_pnl"] for a in analytics]
    return df

def calendar_layout(year: int, month: int, user_id: int, account_id: int) -> html.Div:
    # Generate all days to display in the calendar grid (including leading/trailing days for full weeks)
    cal = calendar.Calendar()
    month_days = list(cal.itermonthdates(year, month))
    df = get_trades_by_day(year, month, user_id, account_id)
    # Group by day
    day_stats = df.groupby("date").agg(
        pnl=("realized_pnl", "sum"),
        trades=("id", "count")
    ).reset_index()
    day_stats = day_stats.set_index("date")
    # Build calendar grid with weekly summary to the right
    weeks = []
    week_summaries = []
    for week in range(0, len(month_days), 7):
        days = []
        week_days = [d for d in month_days[week:week+7] if d.month == month]
        for d in month_days[week:week+7]:
            if d.month != month:
                days.append(html.Td("", style={"background": "#f8f9fa"}))
            else:
                pnl = day_stats.loc[d, "pnl"] if d in day_stats.index else 0
                ntrades = day_stats.loc[d, "trades"] if d in day_stats.index else 0
                color = "green" if pnl > 0 else ("red" if pnl < 0 else "#888")
                days.append(html.Td([
                    html.Div(str(d.day), style={"position": "absolute", "top": 4, "right": 8, "fontSize": "0.95em", "color": "#888"}),
                    html.Div(f"${pnl:.0f}", style={"color": color, "fontWeight": "bold", "marginTop": "18px"}),
                    html.Div(f"{ntrades} Trade{'s' if ntrades != 1 else ''}", style={"fontSize": "0.9em"})
                ], style={"padding": "8px", "border": "1px solid #ddd", "textAlign": "center", "position": "relative", "height": "64px", "verticalAlign": "top"}))
        # Weekly summary for this week
        week_df = df[df["date"].isin(week_days)]
        pnl = week_df["realized_pnl"].sum()
        wins = (week_df["realized_pnl"] > 0).sum()
        losses = (week_df["realized_pnl"] < 0).sum()
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        summary_box = html.Div([
            html.Div(f"P&L: ${pnl:.0f}", style={"color": "green" if pnl > 0 else ("red" if pnl < 0 else "#888"), "fontWeight": "bold"}),
            html.Div(f"Win Rate: {win_rate:.0f}%"),
            html.Div(f"Wins: {wins}  Losses: {losses}")
        ], style={
            "border": "2px solid #b8b8b8",
            "borderRadius": "8px",
            "padding": "8px 10px",
            "marginLeft": "8px",
            "background": "#f5f5f5",
            "minWidth": "110px",
            "fontSize": "0.97em",
            "textAlign": "left"
        })
        # Add the summary as the last (rightmost) cell in the week row
        days.append(html.Td(summary_box, style={"verticalAlign": "top", "background": "#f8f9fa"}))
        weeks.append(html.Tr(days))
    # Month navigation
    prev_month = (date(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month = (date(year, month, 28) + timedelta(days=4)).replace(day=1)
    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Button("<", id="cal-prev-month", n_clicks=0, color="secondary", outline=True, size="sm"), width="auto"),
            dbc.Col(html.H4(f"{calendar.month_name[month]} {year}", className="text-center"), width=8),
            dbc.Col(dbc.Button(">", id="cal-next-month", n_clicks=0, color="secondary", outline=True, size="sm"), width="auto"),
        ], align="center", className="mb-2 g-2 justify-content-center"),
        html.Table([
            html.Thead(html.Tr([
                *[html.Th(day) for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]],
                html.Th("Weekly Summary")
            ])),
            html.Tbody(weeks)
        ], style={"width": "100%", "marginBottom": "16px"}),
    ])

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Trade Craft", className="text-light"), width="auto"),
        dbc.Col(user_account_dropdowns(), width="auto", style={"marginLeft": "auto"}),
    ], className="align-items-center mb-4 g-0"),
    dcc.Store(id="cal-year", data=date.today().year),
    dcc.Store(id="cal-month", data=date.today().month),
    html.Div(id="calendar-content")
], fluid=True)

@callback(
    Output("calendar-content", "children"),
    [Input("cal-year", "data"),
     Input("cal-month", "data"),
     Input("user-dropdown", "value"),
     Input("account-dropdown", "value")],
)
def update_calendar(year, month, user_id, account_id):
    return calendar_layout(year, month, user_id, account_id)

@callback(
    Output("cal-year", "data", allow_duplicate=True),
    Output("cal-month", "data", allow_duplicate=True),
    Input("cal-prev-month", "n_clicks"),
    Input("cal-next-month", "n_clicks"),
    State("cal-year", "data"),
    State("cal-month", "data"),
    prevent_initial_call=True
)
def change_month(prev_clicks, next_clicks, year, month):
    ctx = dash.callback_context
    if not ctx.triggered:
        return year, month
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    if btn == "cal-prev-month":
        prev = (date(year, month, 1) - timedelta(days=1))
        return prev.year, prev.month
    elif btn == "cal-next-month":
        next_ = (date(year, month, 28) + timedelta(days=4))
        return next_.year, next_.month
    return year, month
