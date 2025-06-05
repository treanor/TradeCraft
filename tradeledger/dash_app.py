import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_ag_grid as dag
import plotly.graph_objs as go
import pandas as pd
import db
from datetime import datetime, timedelta

# --- Fetch trades data (using your db.py) ---
def get_trades():
    trades_df = db.fetch_trades()
    if trades_df.empty:
        # Ensure all required columns exist even if empty
        cols = ['date','ticker','pnl','side','quantity','price','notes','tags']
        for col in cols:
            if col not in trades_df:
                trades_df[col] = []
        return trades_df
    trades_df = trades_df.copy()
    trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
    trades_df['Symbol'] = trades_df['ticker']
    trades_df['Status'] = trades_df['pnl'].apply(lambda x: 'WIN' if x > 0 else ('LOSS' if x < 0 else 'WASH'))
    trades_df['Side'] = trades_df['side']
    trades_df['Qty'] = trades_df['quantity']
    trades_df['Entry'] = trades_df['price']
    trades_df['Exit'] = trades_df['price']  # Placeholder
    trades_df['Ent Tot'] = trades_df['price'] * trades_df['quantity']
    trades_df['Ext Tot'] = trades_df['price'] * trades_df['quantity']  # Placeholder
    trades_df['Pos'] = '-'
    trades_df['Hold'] = '-'
    trades_df['Return'] = trades_df['pnl']
    trades_df['Return %'] = trades_df.apply(lambda row: (row['pnl'] / (row['price'] * row['quantity'])) * 100 if row['price'] * row['quantity'] != 0 else 0, axis=1)
    # Ensure notes and tags columns exist
    if 'notes' not in trades_df:
        trades_df['notes'] = ''
    if 'tags' not in trades_df:
        trades_df['tags'] = ''
    return trades_df

# --- App Setup ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'TradeLedger'

# --- App Layout (no html.Style, CSS is in assets/custom.css) ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        # Sidebar
        html.Div([
            html.Div([
                html.Div('Default Account', className='account-label'),
                html.Div([
                    html.Span('$788.00', className='balance'),
                ], className='balance'),
                html.Div([
                    html.Div(['Cash: ', html.Span('-$1,185.00', className='cash')]),
                    html.Div(['Active: ', html.Span('$1,973.00', className='active')]),
                ], className='account-details'),
            ], className='account'),
            html.Div([
                html.Div([
                    html.Span('📊', className='nav-icon'), 'Dashboard'
                ], className='nav-item active', id='nav-dashboard', n_clicks=0),
                html.Div([
                    html.Span('📈', className='nav-icon'), 'Stats'
                ], className='nav-item', id='nav-stats', n_clicks=0),
                html.Div([
                    html.Span('📅', className='nav-icon'), 'Calendar'
                ], className='nav-item', id='nav-calendar', n_clicks=0),
                html.Div([
                    html.Span('⚙️', className='nav-icon'), 'Settings'
                ], className='nav-item', id='nav-settings', n_clicks=0),
                html.Div([
                    html.Span('❓', className='nav-icon'), 'Help'
                ], className='nav-item', id='nav-help', n_clicks=0),
            ], className='nav'),
            html.Button('⬛ New Trade', className='action-btn btn-trade'),
            html.Button('🗂️ New Setup', className='action-btn btn-setup'),
            html.Button('📎 New Note', className='action-btn btn-note'),
        ], className='sidebar'),
        # Header
        html.Div([
            html.Span('📊', className='logo'),
            html.Span('TradeLedger', className='title'),
        ], className='header'),
        # Main Content
        html.Div(id='page-content', className='main-content'),
    ])
])

# --- Callbacks for navigation and content ---
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    try:
        trades_df = get_trades()
        if pathname in ['/', '/dashboard']:
            # Stat cards
            wins = (trades_df['pnl'] > 0).sum() if not trades_df.empty else 0
            losses = (trades_df['pnl'] < 0).sum() if not trades_df.empty else 0
            washes = (trades_df['pnl'] == 0).sum() if not trades_df.empty else 0
            open_trades = 2
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if wins else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losses else 0
            pnl = trades_df['pnl'].sum() if not trades_df.empty else 0
            stat_cards = html.Div([
                html.Div([
                    html.Div('Wins', className='stat-title'),
                    html.Div(str(wins), className='stat-value stat-pos')
                ], className='stat-card'),
                html.Div([
                    html.Div('Losses', className='stat-title'),
                    html.Div(str(losses), className='stat-value stat-neg')
                ], className='stat-card'),
                html.Div([
                    html.Div('Open', className='stat-title'),
                    html.Div(str(open_trades), className='stat-value stat-pos')
                ], className='stat-card'),
                html.Div([
                    html.Div('Wash', className='stat-title'),
                    html.Div(str(washes), className='stat-value stat-neutral')
                ], className='stat-card'),
                html.Div([
                    html.Div('Avg W', className='stat-title'),
                    html.Div(f"${avg_win:.0f}", className='stat-value stat-pos')
                ], className='stat-card'),
                html.Div([
                    html.Div('Avg L', className='stat-title'),
                    html.Div(f"${avg_loss:.0f}", className='stat-value stat-neg')
                ], className='stat-card'),
                html.Div([
                    html.Div('PnL', className='stat-title'),
                    html.Div(f"${pnl:.2f}", className='stat-value')
                ], className='stat-card'),
            ], style={'display': 'flex', 'gap': '1em', 'marginBottom': '2em'})
            # Performance chart
            if not trades_df.empty:
                trades_df_sorted = trades_df.sort_values('date')
                trades_df_sorted['cum_pnl'] = trades_df_sorted['pnl'].cumsum()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trades_df_sorted['date'], y=trades_df_sorted['cum_pnl'], mode='lines+markers', name='PnL', line=dict(color='#4ade80')))
                fig.update_layout(
                    plot_bgcolor='#23283a',
                    paper_bgcolor='#23283a',
                    font_color='#e0e6f0',
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=220,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False),
                )
                chart = dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'marginBottom': '2em'})
            else:
                chart = html.Div('No trades to display.', style={'color': '#aaa', 'marginBottom': '2em'})
            # Trades Table
            if not trades_df.empty:
                status_renderer_js = """
                function(params) {
                    if (params.value === 'WIN') return `<span style=\"background:#14532d;color:#4ade80;padding:2px 10px;border-radius:8px;\">WIN</span>`;
                    if (params.value === 'LOSS') return `<span style=\"background:#7f1d1d;color:#f87171;padding:2px 10px;border-radius:8px;\">LOSS</span>`;
                    return `<span style=\"background:#78350f;color:#facc15;padding:2px 10px;border-radius:8px;\">WASH</span>`;
                }
                """
                return_renderer_js = """
                function(params) {
                    let color = params.value > 0 ? '#4ade80' : (params.value < 0 ? '#f87171' : '#facc15');
                    return `<span style=\"color:${color}\">$${params.value.toFixed(2)}</span>`;
                }
                """
                return_pct_renderer_js = """
                function(params) {
                    let color = params.value > 0 ? '#4ade80' : (params.value < 0 ? '#f87171' : '#facc15');
                    return `<span style=\"color:${color}\">${params.value.toFixed(2)}%</span>`;
                }
                """
                column_defs = [
                    {"headerName": "Date", "field": "date", "width": 110},
                    {"headerName": "Symbol", "field": "Symbol", "width": 120},
                    {"headerName": "Status", "field": "Status", "width": 90, "cellRenderer": status_renderer_js},
                    {"headerName": "Side", "field": "Side", "width": 80},
                    {"headerName": "Qty", "field": "Qty", "width": 70},
                    {"headerName": "Entry", "field": "Entry", "width": 90},
                    {"headerName": "Exit", "field": "Exit", "width": 90},
                    {"headerName": "Ent Tot", "field": "Ent Tot", "width": 110},
                    {"headerName": "Ext Tot", "field": "Ext Tot", "width": 110},
                    {"headerName": "Pos", "field": "Pos", "width": 70},
                    {"headerName": "Hold", "field": "Hold", "width": 90},
                    {"headerName": "Return", "field": "Return", "width": 90, "cellRenderer": return_renderer_js},
                    {"headerName": "Return %", "field": "Return %", "width": 90, "cellRenderer": return_pct_renderer_js},
                    {"headerName": "Notes", "field": "notes", "width": 120},
                    {"headerName": "Tags", "field": "tags", "width": 120},
                ]
                ag_grid = dag.AgGrid(
                    id='trades-table',
                    columnDefs=column_defs,
                    rowData=trades_df.to_dict('records'),
                    dashGridOptions={"domLayout": "normal"},
                    defaultColDef={"resizable": True, "sortable": True},
                    style={"height": 400, "width": "100%", "background": "#23283a", "color": "#e0e6f0"},
                    dangerously_allow_code=True
                )
            else:
                ag_grid = html.Div()
            return html.Div([
                stat_cards,
                chart,
                html.H4('Trades', style={'marginTop': '2em', 'color': '#e0e6f0'}),
                ag_grid
            ])
        elif pathname == '/stats':
            return html.Div('Stats page coming soon.', style={'color': '#aaa'})
        elif pathname == '/calendar':
            return html.Div('Calendar page coming soon.', style={'color': '#aaa'})
        elif pathname == '/settings':
            return html.Div('Settings page coming soon.', style={'color': '#aaa'})
        elif pathname == '/help':
            return html.Div('Help page coming soon.', style={'color': '#aaa'})
        else:
            return html.Div('Page not found.', style={'color': '#f87171'})
    except Exception as e:
        return html.Div(f'Error: {str(e)}', style={'color': '#f87171'})

if __name__ == '__main__':
    app.run(debug=True)
