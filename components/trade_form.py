"""
Reusable trade form component for adding/editing trades.
"""
from dash import html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Dict, Any, Optional

def trade_form_modal(modal_id: str = "trade-modal", is_edit: bool = False) -> dbc.Modal:
    """
    Create a modal with trade form for adding or editing trades.
    Args:
        modal_id: Unique ID for the modal.
        is_edit: Whether this is for editing (True) or adding (False) a trade.
    Returns:
        dbc.Modal component.
    """
    title = "Edit Trade" if is_edit else "Add New Trade"
    submit_text = "Update" if is_edit else "Save"
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(title)),
        dbc.ModalBody([
            dbc.Form([
                # Basic trade information
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Market", className="mb-1"),
                        dbc.Select(
                            id=f"{modal_id}-market",
                            options=[
                                {"label": "Stock", "value": "stock"},
                                {"label": "Option", "value": "option"},
                                {"label": "Future", "value": "future"},
                                {"label": "Crypto", "value": "crypto"},
                                {"label": "Forex", "value": "forex"},
                                {"label": "Other", "value": "other"},
                            ],
                            value="stock",
                            style={"fontSize": "1.05rem"}
                        ),
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Symbol", className="mb-1"),
                        dbc.Input(
                            id=f"{modal_id}-symbol", 
                            type="text", 
                            required=True, 
                            placeholder="e.g., AAPL",
                            style={"fontSize": "1.05rem"}
                        ),
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Tags", className="mb-1"),
                        dbc.Input(
                            id=f"{modal_id}-tags",
                            type="text",
                            placeholder="swing, earnings, etc.",
                            style={"fontSize": "1.05rem"}
                        ),
                    ], width=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Notes", className="mb-1"),
                        dbc.Textarea(
                            id=f"{modal_id}-notes",
                            placeholder="Trade journal notes...",
                            style={"height": "80px", "fontSize": "1.05rem"}
                        ),
                    ], width=12),
                ], className="mb-3"),
                
                html.Hr(className="my-3"),
                
                # Trade legs section
                html.H5("Trade Legs", className="mb-3"),
                html.Div(
                    id=f"{modal_id}-legs-container",
                    style={
                        "background": "#f8f9fa",
                        "border": "1px solid #e2e3e5",
                        "borderRadius": "8px",
                        "padding": "16px",
                        "marginBottom": "16px",
                    }
                ),
                
                dbc.Row([
                    dbc.Col([], width=9),
                    dbc.Col([
                        dbc.Button(
                            "Add Leg", 
                            id=f"{modal_id}-add-leg", 
                            color="primary", 
                            outline=True, 
                            size="sm"
                        ),
                    ], width=3, className="text-end"),
                ], className="mb-2"),
                
                # Hidden store for legs data
                dcc.Store(id=f"{modal_id}-legs-store", data=[]),
                dcc.Store(id=f"{modal_id}-trade-id", data=None),  # For edit mode
            ]),
        ]),
        dbc.ModalFooter([
            dbc.Button(
                submit_text, 
                id=f"{modal_id}-submit", 
                color="success", 
                className="me-2"
            ),
            dbc.Button(
                "Cancel", 
                id=f"{modal_id}-cancel", 
                color="secondary"
            ),
        ]),
    ], id=modal_id, is_open=False, size="xl")

def trade_leg_row(leg_data: Dict[str, Any], index: int, modal_id: str) -> dbc.Row:
    """
    Create a single trade leg row.
    Args:
        leg_data: Dictionary containing leg information.
        index: Index of the leg.
        modal_id: Modal ID for unique component IDs.
    Returns:
        dbc.Row component.
    """
    return dbc.Row([
        dbc.Col([
            dbc.Button(
                "×", 
                id={"type": f"{modal_id}-remove-leg", "index": index},
                color="danger", 
                size="sm",
                style={"width": "30px", "height": "30px", "padding": "0"}
            ),
        ], width=1),
        dbc.Col([
            dbc.Select(
                id={"type": f"{modal_id}-leg-action", "index": index},
                options=[
                    {"label": "BUY", "value": "buy"},
                    {"label": "SELL", "value": "sell"},
                    {"label": "BUY TO OPEN", "value": "buy to open"},
                    {"label": "SELL TO CLOSE", "value": "sell to close"},
                ],
                value=leg_data.get("action", "buy"),
                size="sm"
            ),
        ], width=2),
        dbc.Col([
            dcc.DatePickerSingle(
                id={"type": f"{modal_id}-leg-date", "index": index},
                date=leg_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                display_format="YYYY-MM-DD",
                style={"width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": f"{modal_id}-leg-time", "index": index},
                type="time",
                value=leg_data.get("time", "09:30"),
                size="sm"
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": f"{modal_id}-leg-quantity", "index": index},
                type="number",
                value=leg_data.get("quantity", 1),
                min=1,
                size="sm"
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": f"{modal_id}-leg-price", "index": index},
                type="number",
                value=leg_data.get("price", 1.0),
                min=0,
                step=0.01,
                size="sm"
            ),
        ], width=2),
        dbc.Col([
            dbc.Input(
                id={"type": f"{modal_id}-leg-fees", "index": index},
                type="number",
                value=leg_data.get("fees", 0.0),
                min=0,
                step=0.01,
                size="sm"
            ),
        ], width=1),
    ], className="mb-2 align-items-center")

def render_legs_table(legs: List[Dict[str, Any]], modal_id: str) -> html.Div:
    """
    Render the complete legs table with headers and rows.
    Args:
        legs: List of leg dictionaries.
        modal_id: Modal ID for unique component IDs.
    Returns:
        html.Div containing the legs table.
    """
    if not legs:
        return html.Div("No legs added. Click 'Add Leg' to start.", className="text-muted")
    
    # Header row
    header = dbc.Row([
        dbc.Col("", width=1),  # Remove button column
        dbc.Col("Action", width=2, className="fw-bold"),
        dbc.Col("Date", width=2, className="fw-bold"),
        dbc.Col("Time", width=2, className="fw-bold"),
        dbc.Col("Quantity", width=2, className="fw-bold"),
        dbc.Col("Price", width=2, className="fw-bold"),
        dbc.Col("Fees", width=1, className="fw-bold"),
    ], className="mb-2")
    
    # Data rows
    rows = [trade_leg_row(leg, i, modal_id) for i, leg in enumerate(legs)]
    
    return html.Div([header] + rows)

def validate_trade_form(symbol: str, legs: List[Dict[str, Any]]) -> tuple[bool, str]:
    """
    Validate trade form data.
    Args:
        symbol: Trade symbol.
        legs: List of trade legs.
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not symbol or not symbol.strip():
        return False, "Symbol is required"
    
    if not legs or len(legs) == 0:
        return False, "At least one trade leg is required"
    
    for i, leg in enumerate(legs):
        if not leg.get("quantity") or leg["quantity"] <= 0:
            return False, f"Leg {i+1}: Quantity must be greater than 0"
        
        if not leg.get("price") or leg["price"] <= 0:
            return False, f"Leg {i+1}: Price must be greater than 0"
        
        if not leg.get("date"):
            return False, f"Leg {i+1}: Date is required"
    
    return True, ""