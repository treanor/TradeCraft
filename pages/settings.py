"""
Settings Page for Trade Craft
- Allows user selection (persisted across app)
"""
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from utils import db_access

# Register page
dash.register_page(__name__, path="/settings", name="Settings")

def get_user_options():
    users = db_access.get_all_users()
    return [{"label": u["username"], "value": u["id"]} for u in users]

layout = dbc.Container([
    dcc.Store(id="user-store", storage_type="local"),
    html.H2("Settings", className="mb-4 mt-2"),
    dbc.Row([
        dbc.Col([
            html.Label("Select User", className="mb-2"),
            dcc.Dropdown(
                id="settings-user-dropdown",
                options=get_user_options(),
                value=None,
                clearable=False,
                style={"minWidth": 200},
            ),
            html.Div(id="settings-user-save-msg", className="mt-2"),
        ], width=6),
    ]),
    dbc.Button("Save", id="settings-save-user", color="primary", className="mt-3"),
])

@callback(
    Output("settings-user-save-msg", "children"),
    Output("user-store", "data"),
    Input("settings-save-user", "n_clicks"),
    State("settings-user-dropdown", "value"),
    prevent_initial_call=True
)
def save_user_selection(n_clicks: int, user_id: int):
    if user_id is not None:
        return "User selection saved!", user_id
    return "Please select a user.", dash.no_update
