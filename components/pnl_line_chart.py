import pandas as pd
import plotly.graph_objs as go


def pnl_over_time_figure(df: pd.DataFrame) -> go.Figure:
    """
    Return a Plotly figure of cumulative P&L over time (neon/dark theme).
    Args:
        df (pd.DataFrame): DataFrame with at least 'opened_at' and 'realized_pnl' columns.
    Returns:
        go.Figure: Plotly line chart of cumulative P&L.
    """
    if df.empty or "opened_at" not in df or "realized_pnl" not in df:
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
