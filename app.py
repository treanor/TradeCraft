"""
Trade Craft Dash App Entry Point

- Multi-page support using dash.page_registry
- Basic navigation bar and layout
"""
import dash
from dash import html, dcc
import importlib
import os
from components.header import Header

# Register pages from the /pages directory automatically
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Trade Craft Journal"
)

# App layout with navigation and page container
app.layout = html.Div([
    dcc.Location(id="url-redirector", refresh=True),
    Header(),
    dash.page_container
])

# Redirect from / to /trade_log
from dash.dependencies import Input, Output
@app.callback(
    Output("url-redirector", "pathname"),
    Input("url-redirector", "pathname"),
    prevent_initial_call=True
)
def redirect_root(pathname):
    if pathname == "/":
        return "/trade_log"
    return dash.no_update

if __name__ == "__main__":
    app.run_server(debug=True)
