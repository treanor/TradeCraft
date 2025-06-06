import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_ag_grid as dag
import plotly.graph_objs as go
import pandas as pd
import db
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from dash import ALL
import json

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
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
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
            html.Button('⬛ New Trade', className='action-btn btn-trade', id='btn-new-trade', n_clicks=0),
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
        # New Trade Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle('New Trade'), close_button=True),
            dbc.ModalBody([
                dbc.Tabs([
                    dbc.Tab(label='General', tab_id='tab-general'),
                    dbc.Tab(label='Journal', tab_id='tab-journal'),
                ], id='trade-modal-tabs', active_tab='tab-general'),
                html.Div(id='trade-modal-content')
            ]),
            dbc.ModalFooter([
                dbc.Button('Save', id='btn-save-trade', color='primary', className='ms-auto')
            ])
        ], id='modal-new-trade', is_open=False, size='xl', backdrop='static', centered=True),
        # Trade Details Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle('Trade Details'), close_button=True),
            dbc.ModalBody(id='trade-details-body'),
        ], id='modal-trade-details', is_open=False, size='lg', backdrop='static', centered=True)
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
                symbol_renderer_js = """
                function(params) {
                    return `<a href='#' style=\"color:#60a5fa;text-decoration:underline;cursor:pointer;font-weight:500;\">${params.value}</a>`;
                }
                """
                column_defs = [
                    {"headerName": "Date", "field": "date", "width": 110},
                    {"headerName": "Symbol", "field": "Symbol", "width": 120, "cellRenderer": symbol_renderer_js},
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
                    dashGridOptions={
                        "domLayout": "normal",
                        "rowSelection": "single",
                        "suppressRowClickSelection": False,
                        "suppressCellFocus": False,
                        "rowClass": "trade-row",
                        "onCellClicked": {'function': 'function(e) { if(e.colDef.field === \"Symbol\") { window.dash_clientside.callback_context.triggered.push({prop_id: `trades-table.cellClicked`}); } }'}
                    },
                    defaultColDef={"resizable": True, "sortable": True},
                    style={"height": 400, "width": "100%", "background": "#23283a", "color": "#e0e6f0"},
                    dangerously_allow_code=True,
                    selectedRows=[],
                )
            else:
                ag_grid = html.Div()
            # Details modal (hidden by default)
            details_modal = dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle('Trade Details'), close_button=True),
                dbc.ModalBody(id='trade-details-body'),
            ], id='modal-trade-details', is_open=False, size='lg', backdrop='static', centered=True)
            return html.Div([
                stat_cards,
                chart,
                html.H4('Trades', style={'marginTop': '2em', 'color': '#e0e6f0'}),
                ag_grid,
                details_modal
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

# --- Callbacks for modal open/close ---
@app.callback(
    Output('modal-new-trade', 'is_open'),
    [Input('btn-new-trade', 'n_clicks')],
    [State('modal-new-trade', 'is_open')]
)
def toggle_new_trade_modal(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

# --- Callback for modal content (General tab) ---
@app.callback(
    Output('trade-modal-content', 'children'),
    [Input('trade-modal-tabs', 'active_tab')]
)
def render_trade_modal_content(tab):
    if tab == 'tab-general':
        return [
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Select(options=[{"label": "OPTION", "value": "OPTION"}, {"label": "STOCK", "value": "STOCK"}], value="OPTION", id="trade-market"), width=2),
                    dbc.Col(dbc.Input(placeholder="SPY", id="trade-symbol", value="SPY"), width=2),
                    dbc.Col(dbc.Input(placeholder="Target", id="trade-target"), width=2),
                    dbc.Col(dbc.Input(placeholder="Stop-Loss", id="trade-stoploss"), width=2),
                    dbc.Col(dbc.Button("LONG", id="trade-longshort", color="success", outline=False, style={"width": "100%"}), width=2),
                ], className="mb-3"),
                # Table header
                html.Div([
                    html.Div("Action", className="trade-table-header"),
                    html.Div("Date/ Time", className="trade-table-header"),
                    html.Div("Quantity", className="trade-table-header"),
                    html.Div("Price", className="trade-table-header"),
                    html.Div("Fee", className="trade-table-header"),
                ], className="trade-table-row trade-table-header-row"),
                # Table rows (initial, dynamic rows to be added in next step)
                html.Div(id="trade-legs-rows"),
                # Add row button
                html.Div([
                    dbc.Button("+", id="btn-add-leg", color="primary", outline=True, size="sm")
                ], style={"textAlign": "center", "marginTop": "1em"})
            ], className="trade-modal-form")
        ]
    elif tab == 'tab-journal':
        return dbc.Textarea(id="trade-journal", placeholder="Journal notes...", style={"width": "100%", "minHeight": "200px"})
    return None

# --- Initial trade legs state ---
def initial_trade_legs():
    now = datetime.now().strftime('%m/%d/%Y %I:%M %p')
    return [
        {"action": "BUY", "datetime": now, "quantity": 1, "price": 12, "fee": 0},
        {"action": "SELL", "datetime": now, "quantity": 1, "price": 23, "fee": 0},
    ]

# --- Callback to manage trade legs rows ---
@app.callback(
    Output('trade-legs-rows', 'children'),
    [Input('btn-add-leg', 'n_clicks')],
    [State({'type': 'trade-leg-action', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-datetime', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-quantity', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-price', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-fee', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_trade_legs(add_click, actions, datetimes, quantities, prices, fees):
    ctx = callback_context
    if not ctx.triggered or all(x is None for x in [actions, datetimes, quantities, prices, fees]):
        legs = initial_trade_legs()
    else:
        legs = [
            {"action": a, "datetime": d, "quantity": q, "price": p, "fee": f}
            for a, d, q, p, f in zip(actions, datetimes, quantities, prices, fees)
        ]
        if ctx.triggered[0]['prop_id'].startswith('btn-add-leg'):
            now = datetime.now().strftime('%m/%d/%Y %I:%M %p')
            legs.append({"action": "BUY", "datetime": now, "quantity": 1, "price": 0, "fee": 0})
    return [
        html.Div([
            dbc.Button("✖", id={'type': 'btn-remove-leg', 'index': i}, color='danger', outline=True, size='sm', className='me-2'),
            dbc.Button("BUY" if leg["action"] == "BUY" else "SELL", id={'type': 'trade-leg-action', 'index': i}, color='success' if leg["action"] == "BUY" else 'danger', outline=False, style={"width": "70px"}, value=leg["action"]),
            dbc.Input(type='text', value=leg["datetime"], id={'type': 'trade-leg-datetime', 'index': i}, style={"width": "160px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["quantity"], id={'type': 'trade-leg-quantity', 'index': i}, style={"width": "70px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["price"], id={'type': 'trade-leg-price', 'index': i}, style={"width": "90px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["fee"], id={'type': 'trade-leg-fee', 'index': i}, style={"width": "70px", "marginLeft": "8px"}),
        ], className='trade-table-row', style={"marginBottom": "8px"})
        for i, leg in enumerate(legs)
    ]

# --- Callback to remove a trade leg row ---
@app.callback(
    Output('trade-legs-rows', 'children', allow_duplicate=True),
    [Input({'type': 'btn-remove-leg', 'index': ALL}, 'n_clicks')],
    [State({'type': 'trade-leg-action', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-datetime', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-quantity', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-price', 'index': ALL}, 'value'),
     State({'type': 'trade-leg-fee', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def remove_trade_leg(remove_clicks, actions, datetimes, quantities, prices, fees):
    ctx = callback_context
    if not ctx.triggered or not remove_clicks:
        return dash.no_update
    # Find which button was clicked
    triggered = [i for i, n in enumerate(remove_clicks) if n]
    if not triggered:
        return dash.no_update
    remove_idx = triggered[0]
    legs = [
        {"action": a, "datetime": d, "quantity": q, "price": p, "fee": f}
        for a, d, q, p, f in zip(actions, datetimes, quantities, prices, fees)
    ]
    if len(legs) > 1:
        legs.pop(remove_idx)
    return [
        html.Div([
            dbc.Button("✖", id={'type': 'btn-remove-leg', 'index': i}, color='danger', outline=True, size='sm', className='me-2'),
            dbc.Button("BUY" if leg["action"] == "BUY" else "SELL", id={'type': 'trade-leg-action', 'index': i}, color='success' if leg["action"] == "BUY" else 'danger', outline=False, style={"width": "70px"}, value=leg["action"]),
            dbc.Input(type='text', value=leg["datetime"], id={'type': 'trade-leg-datetime', 'index': i}, style={"width": "160px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["quantity"], id={'type': 'trade-leg-quantity', 'index': i}, style={"width": "70px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["price"], id={'type': 'trade-leg-price', 'index': i}, style={"width": "90px", "marginLeft": "8px"}),
            dbc.Input(type='number', value=leg["fee"], id={'type': 'trade-leg-fee', 'index': i}, style={"width": "70px", "marginLeft": "8px"}),
        ], className='trade-table-row', style={"marginBottom": "8px"})
        for i, leg in enumerate(legs)
    ]

# --- Callback to toggle LONG/SHORT button ---
@app.callback(
    Output('trade-longshort', 'children'),
    Output('trade-longshort', 'color'),
    [Input('trade-longshort', 'n_clicks')],
    [State('trade-longshort', 'children')],
    prevent_initial_call=True
)
def toggle_longshort(n_clicks, current):
    if n_clicks is None:
        return 'LONG', 'success'
    if current == 'LONG':
        return 'SHORT', 'danger'
    else:
        return 'LONG', 'success'

# --- Callback to toggle BUY/SELL for each trade leg ---
@app.callback(
    Output({'type': 'trade-leg-action', 'index': ALL}, 'children'),
    Output({'type': 'trade-leg-action', 'index': ALL}, 'color'),
    [Input({'type': 'trade-leg-action', 'index': ALL}, 'n_clicks')],
    [State({'type': 'trade-leg-action', 'index': ALL}, 'children')],
    prevent_initial_call=True
)
def toggle_leg_action(n_clicks, current):
    ctx = callback_context
    if not current or not ctx.triggered:
        return dash.no_update, dash.no_update
    # Find which button was clicked
    triggered_idx = None
    for i, n in enumerate(n_clicks):
        if n and (n == max([x for x in n_clicks if x is not None])):
            triggered_idx = i
            break
    if triggered_idx is None:
        return dash.no_update, dash.no_update
    # Only toggle the clicked button
    toggled = []
    colors = []
    for i, c in enumerate(current):
        if i == triggered_idx:
            if c == 'BUY':
                toggled.append('SELL')
                colors.append('danger')
            else:
                toggled.append('BUY')
                colors.append('success')
        else:
            toggled.append(c)
            colors.append('success' if c == 'BUY' else 'danger')
    return toggled, colors

# --- Callback for Save button in New Trade modal ---
@app.callback(
    Output('modal-new-trade', 'is_open', allow_duplicate=True),
    [Input('btn-save-trade', 'n_clicks')],
    [
        State('trade-market', 'value'),
        State('trade-symbol', 'value'),
        State('trade-target', 'value'),
        State('trade-stoploss', 'value'),
        State('trade-longshort', 'children'),
        State({'type': 'trade-leg-action', 'index': ALL}, 'children'),
        State({'type': 'trade-leg-datetime', 'index': ALL}, 'value'),
        State({'type': 'trade-leg-quantity', 'index': ALL}, 'value'),
        State({'type': 'trade-leg-price', 'index': ALL}, 'value'),
        State({'type': 'trade-leg-fee', 'index': ALL}, 'value'),
        State('trade-modal-tabs', 'active_tab'),
        State('trade-modal-content', 'children'),
        State('modal-new-trade', 'is_open')
    ],
    prevent_initial_call=True
)
def save_new_trade(save_click, market, symbol, target, stoploss, longshort, actions, datetimes, quantities, prices, fees, active_tab, modal_content, is_open):
    if not save_click:
        return is_open
    # Try to extract journal value if on journal tab
    journal = ''
    if active_tab == 'tab-journal' and modal_content:
        for child in modal_content:
            if hasattr(child, 'props') and child.props.get('id') == 'trade-journal':
                journal = child.props.get('value', '')
    # Save as a single trade with all legs as JSON
    import db
    legs = []
    for a, d, q, p, f in zip(actions, datetimes, quantities, prices, fees):
        legs.append({
            'action': a,
            'datetime': d,
            'quantity': q,
            'price': p,
            'fee': f
        })
    db.add_trade(
        date=datetimes[0] if datetimes else str(datetime.now().date()),
        ticker=symbol,
        side=longshort,
        quantity=sum([int(q) for q in quantities if q]),
        price=legs[0]['price'] if legs else 0,
        pnl=0,  # You may want to calculate this later
        notes=journal or '',
        tags=f"{market},{longshort}",
        legs=json.dumps(legs)
    )
    return False  # Close modal after save

# --- Add a details modal for trade view ---
app.layout.children.append(
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Trade Details'), close_button=True),
        dbc.ModalBody(id='trade-details-body'),
    ], id='modal-trade-details', is_open=False, size='lg', backdrop='static', centered=True)
)

# --- CALLBACK: Open trade details modal on Symbol click ---
@app.callback(
    Output('modal-trade-details', 'is_open'),
    Output('trade-details-body', 'children'),
    Input('trades-table', 'cellClicked'),
    State('trades-table', 'rowData'),
    State('modal-trade-details', 'is_open'),
    prevent_initial_call=True
)
def open_trade_details(cellClicked, rowData, is_open):
    if cellClicked and cellClicked.get('colDef', {}).get('field') == 'Symbol':
        row_idx = cellClicked.get('rowIndex')
        if row_idx is not None and rowData and row_idx < len(rowData):
            trade = rowData[row_idx]
            # Parse legs JSON if present
            import json
            legs = []
            if 'legs' in trade and trade['legs']:
                try:
                    legs = json.loads(trade['legs'])
                except Exception:
                    legs = []
            # Build details UI
            details = [
                html.H5(f"{trade.get('Symbol', '')} | {trade.get('date', '')}", style={"color": "#60a5fa"}),
                html.P(f"Status: {trade.get('Status', '')} | Side: {trade.get('Side', '')} | Qty: {trade.get('Qty', '')}"),
                html.P(f"Entry: {trade.get('Entry', '')} | Exit: {trade.get('Exit', '')}"),
                html.P(f"Return: ${trade.get('Return', 0):,.2f} ({trade.get('Return %', 0):.2f}%)"),
                html.P(f"Notes: {trade.get('notes', '')}"),
                html.P(f"Tags: {trade.get('tags', '')}"),
            ]
            if legs:
                details.append(html.H6("Legs:"))
                details.append(dbc.Table([
                    html.Thead(html.Tr([html.Th(k) for k in legs[0].keys()])),
                    html.Tbody([
                        html.Tr([html.Td(str(leg.get(k, ''))) for k in legs[0].keys()]) for leg in legs
                    ])
                ], bordered=True, size='sm', style={"background": "#23283a", "color": "#e0e6f0"}))
            return True, details
    return False, dash.no_update

# --- CALLBACK: Close trade details modal on close button ---
@app.callback(
    Output('modal-trade-details', 'is_open', allow_duplicate=True),
    Input('modal-trade-details', 'is_open'),
    State('modal-trade-details', 'is_open'),
    prevent_initial_call=True
)
def close_trade_details(is_open_input, is_open_state):
    # This callback is not needed; closing is handled by the open_trade_details callback and the modal's close_button
    return dash.no_update

if __name__ == '__main__':
    app.run(debug=True)
