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

# Register this as a Dash page
# URL: /analytics

dash.register_page(__name__, path="/analytics", name="Analytics")

USERNAME = "alice"  # For now, single-user mode

def get_analytics_df() -> pd.DataFrame:
    """Fetch all trades for the user as a DataFrame with analytics columns."""
    trades = db_access.fetch_trades_for_user(USERNAME)
    if not trades:
        return pd.DataFrame()
    df = pd.DataFrame(trades)
    analytics = [db_access.trade_analytics(row["id"]) for _, row in df.iterrows()]
    df["realized_pnl"] = [a["realized_pnl"] for a in analytics]
    df["status"] = [a["status"] for a in analytics]
    # Robust datetime parsing for ISO8601 and mixed formats
    df["opened_at"] = pd.to_datetime(df["opened_at"], format="mixed", errors="coerce")
    df["asset_type"] = df["asset_type"].fillna("")
    return df

def summary_stats(df: pd.DataFrame) -> list:
    """Return summary stats as a list of html.Divs."""
    if df.empty:
        return [html.Div("No trades to summarize.")]
    total_trades = len(df)
    wins = (df["realized_pnl"] > 0).sum()
    losses = (df["realized_pnl"] < 0).sum()
    open_trades = (df["status"] == "open").sum()
    win_rate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
    avg_win = df.loc[df["realized_pnl"] > 0, "realized_pnl"].mean() or 0
    avg_loss = df.loc[df["realized_pnl"] < 0, "realized_pnl"].mean() or 0
    total_pnl = df["realized_pnl"].sum()
    return [
        html.Div(f"Total Trades: {total_trades}"),
        html.Div(f"Wins: {wins}"),
        html.Div(f"Losses: {losses}"),
        html.Div(f"Open: {open_trades}"),
        html.Div(f"Win Rate: {win_rate:.1f}%"),
        html.Div(f"Avg Win: ${avg_win:.2f}"),
        html.Div(f"Avg Loss: ${avg_loss:.2f}"),
        html.Div(f"Total P&L: ${total_pnl:.2f}"),
    ]

def pnl_over_time_figure(df: pd.DataFrame) -> go.Figure:
    """Return a Plotly figure of cumulative P&L over time."""
    if df.empty:
        return go.Figure()
    df = df.sort_values("opened_at")
    df["cum_pnl"] = df["realized_pnl"].cumsum()
    fig = go.Figure(go.Scatter(
        x=df["opened_at"],
        y=df["cum_pnl"],
        mode="lines+markers",
        name="Equity Curve"
    ))
    fig.update_layout(title="Cumulative P&L Over Time", xaxis_title="Date", yaxis_title="Cumulative P&L", template="plotly_white", height=300)
    return fig

def asset_allocation_figure(df: pd.DataFrame) -> go.Figure:
    """Return a Plotly pie chart of asset allocation by asset_type."""
    if df.empty:
        return go.Figure()
    asset_counts = df["asset_type"].value_counts()
    fig = go.Figure(go.Pie(labels=asset_counts.index, values=asset_counts.values, hole=0.4))
    fig.update_layout(title="Asset Allocation", height=300)
    return fig

layout = dbc.Container([
    html.H2("Analytics / Dashboard"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Summary Stats"),
                dbc.CardBody(id="analytics-summary-stats")
            ]),
        ], width=3),
        dbc.Col([
            dcc.Graph(id="analytics-pnl-curve"),
        ], width=6),
        dbc.Col([
            dcc.Graph(id="analytics-asset-allocation"),
        ], width=3),
    ], className="mb-4"),
], fluid=True)

@callback(
    Output("analytics-summary-stats", "children"),
    Output("analytics-pnl-curve", "figure"),
    Output("analytics-asset-allocation", "figure"),
    Input("analytics-summary-stats", "id")
)
def update_dashboard(_):
    df = get_analytics_df()
    return summary_stats(df), pnl_over_time_figure(df), asset_allocation_figure(df)
