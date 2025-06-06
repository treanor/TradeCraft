# FastAPI backend for TradeCraft sample data
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sample_data import sample_trades
from models import Trade
from stats_utils import get_equity_curve

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper to convert Trade to dashboard row dict ---
def trade_to_row(trade: Trade):
    return trade.to_dashboard_row()

# --- API Endpoints ---

@app.get("/trades", response_model=List[dict])
def get_trades():
    """Get all trades as dashboard rows"""
    return [trade_to_row(t) for t in sample_trades]

@app.get("/trades/{trade_id}")
def get_trade(trade_id: str):
    for t in sample_trades:
        if t.trade_id == trade_id:
            return trade_to_row(t)
    raise HTTPException(status_code=404, detail="Trade not found")

@app.post("/trades", response_model=dict)
def create_trade(trade: dict):
    # This is a stub for now; real DB logic will go here later
    trade['trade_id'] = str(len(sample_trades) + 1)
    # Not actually adding to sample_trades (since it's generated)
    return trade

@app.put("/trades/{trade_id}", response_model=dict)
def update_trade(trade_id: str, trade: dict):
    # This is a stub for now; real DB logic will go here later
    trade['trade_id'] = trade_id
    return trade

@app.delete("/trades/{trade_id}")
def delete_trade(trade_id: str):
    # This is a stub for now; real DB logic will go here later
    return {"deleted": trade_id}

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/equity_curve")
def equity_curve(filter: str = "all"):
    x, y = get_equity_curve(sample_trades, filter)
    return {"x": x, "y": y}
