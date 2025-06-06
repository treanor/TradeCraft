from dash.dependencies import Input, Output, State
from dash import ctx, ALL, html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd
from sample_data import sample_trades
from layout import stats_page_layout, calendar_page_layout, filter_buttons_row
from stats_utils import get_wins, get_losses, get_total_pnl, filter_trades, get_equity_curve

FILTER_OPTIONS = [
    ("All", "all"),
    ("Today", "today"),
    ("Yesterday", "yesterday"),
    ("This wk.", "this_week"),
    ("Last wk.", "last_week"),
    ("This mo.", "this_month"),
]

def register_callbacks(app):
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

    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname"), Input("active-filter", "data"), Input("tag-filter-dropdown", "value")],
    )
    def display_page(pathname, active_filter, selected_tags):
        from sample_data import sample_trades
        from layout import stats_page_layout_dynamic
        if pathname == "/stats":
            trades = filter_trades(sample_trades, active_filter or "this_week", selected_tags)
            return stats_page_layout_dynamic(trades, active_filter or "this_week", selected_tags)
        elif pathname == "/calendar":
            return calendar_page_layout()
        else:
            trades = filter_trades(sample_trades, active_filter or "this_week", selected_tags)
            wins = get_wins(trades)
            losses = get_losses(trades)
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
