"""
Settings Page for Trade Craft
- Allows user selection (persisted across app)
"""
import dash
from dash import html, dcc, callback, Output, Input, State, ctx, no_update
import dash_bootstrap_components as dbc
from utils import db_access
from typing import List, Dict, Any, Tuple, Optional

# Register page
dash.register_page(__name__, path="/settings", name="Settings")

def get_user_options() -> List[Dict[str, Any]]:
    """Get user options for dropdown."""
    users = db_access.get_all_users()
    return [{"label": u["username"], "value": u["id"]} for u in users]

layout = dbc.Container([
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
    Output("settings-user-dropdown", "value"),
    Input("settings-save-user", "n_clicks"),
    Input("user-store", "data"),
    State("settings-user-dropdown", "value"),
    prevent_initial_call=True
)
def handle_settings_page(n_clicks: int, current_user_id: int, selected_user_id: int) -> tuple[str, int]:
    """Handle settings page interactions - save button and dropdown sync."""
    from dash import ctx, no_update
    
    # If user store data changed, update dropdown
    if ctx.triggered_id == "user-store":
        return "", current_user_id or 3  # Default to alice if None
    
    # If save button was clicked
    elif ctx.triggered_id == "settings-save-user" and n_clicks:
        if selected_user_id is not None:
            return "User selection saved!", selected_user_id
        return "Please select a user.", no_update
    
    # Default case
    return no_update, no_update


# Separate callback to update user store when save button is clicked
@callback(
    Output("user-store", "data"),
    Input("settings-save-user", "n_clicks"),
    State("settings-user-dropdown", "value"),
    prevent_initial_call=True
)
def save_user_selection(n_clicks: int, selected_user_id: int) -> int:
    """Save user selection to store."""
    if n_clicks and selected_user_id is not None:
        return selected_user_id
    return dash.no_update
