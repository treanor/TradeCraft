# models.py

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AssetType(Enum):
    STOCK = "stock"
    OPTION = "option"

class TradeAction(Enum):
    # Stock actions
    BUY = "buy"
    SELL = "sell"
    # Option actions
    BUY_TO_OPEN = "buy_to_open"
    BUY_TO_CLOSE = "buy_to_close"
    SELL_TO_OPEN = "sell_to_open"
    SELL_TO_CLOSE = "sell_to_close"
    ASSIGN = "assign"
    EXPIRE = "expire"
    EXERCISE = "exercise"

# Mapping of valid actions by asset type
ACTIONS_BY_ASSET_TYPE = {
    AssetType.STOCK: [TradeAction.BUY, TradeAction.SELL],
    AssetType.OPTION: [
        TradeAction.BUY_TO_OPEN,
        TradeAction.BUY_TO_CLOSE,
        TradeAction.SELL_TO_OPEN,
        TradeAction.SELL_TO_CLOSE,
        TradeAction.ASSIGN,
        TradeAction.EXPIRE,
        TradeAction.EXERCISE,
    ],
}

def get_valid_actions_for_asset_type(asset_type: AssetType):
    return ACTIONS_BY_ASSET_TYPE.get(asset_type, [])

@dataclass
class TradeLeg:
    action: TradeAction           # TradeAction.BUY or TradeAction.SELL
    datetime: datetime
    quantity: float
    price: float
    fee: float = 0.0

@dataclass
class Trade:
    trade_id: str
    user_id: str
    symbol: str
    asset_type: AssetType  # e.g., AssetType.OPTION
    created_at: datetime
    status: str = "OPEN"     # "WIN", "LOSS", or "OPEN"
    journal_entry: Optional[str] = None
    legs: List[TradeLeg] = field(default_factory=list)

    def to_dashboard_row(self):
        # Example: summarize main fields for dashboard table
        entry_leg = self.legs[0] if self.legs else None
        exit_leg = self.legs[1] if len(self.legs) > 1 else None

        # Parse for table fields
        entry_price = entry_leg.price if entry_leg else None
        exit_price = exit_leg.price if exit_leg else None
        qty = entry_leg.quantity if entry_leg else 0

        # Entry/Exit totals
        ent_tot = (entry_leg.quantity * entry_leg.price + entry_leg.fee) if entry_leg else None
        ext_tot = (exit_leg.quantity * exit_leg.price - exit_leg.fee) if exit_leg else None

        # Returns
        ret = (ext_tot - ent_tot) if (ent_tot and ext_tot) else None
        ret_pct = ((ret / ent_tot) * 100) if (ret and ent_tot) else None

        # Hold time
        hold = None
        if entry_leg and exit_leg:
            delta = exit_leg.datetime - entry_leg.datetime
            hold = format_hold(delta)

        # Add time columns for intraday support
        entry_time = entry_leg.datetime.strftime("%H:%M") if entry_leg else "-"
        exit_time = exit_leg.datetime.strftime("%H:%M") if exit_leg else "-"

        return {
            "Date": self.created_at.strftime("%m/%d/%Y"),
            "Time": entry_time,
            "Symbol": self.symbol,
            "Status": self.status,
            "Side": entry_leg.action.value.capitalize() if entry_leg else "-",
            "Qty": int(qty),
            "Entry": f"${entry_price:,.2f}" if entry_price else "-",
            "Exit": f"${exit_price:,.2f}" if exit_price else "-",
            "Ent Tot": f"${ent_tot:,.2f}" if ent_tot else "-",
            "Ext Tot": f"${ext_tot:,.2f}" if ext_tot else "-",
            "Pos": "-",  # Position, fill as needed
            "Hold": hold if hold else "-",
            "Return": f"${ret:,.2f}" if ret else "-",
            "Return %": f"{ret_pct:.2f}%" if ret_pct else "-",
            "Exit Date": exit_leg.datetime.strftime("%m/%d/%Y") if exit_leg else "-",
            "Exit Time": exit_time
        }

def format_hold(td):
    days = td.days
    secs = td.seconds
    hours = secs // 3600
    mins = (secs % 3600) // 60
    if days > 0:
        return f"{days} DAY{'S' if days != 1 else ''}"
    if hours > 0:
        return f"{hours} HR{'S' if hours != 1 else ''}"
    if mins > 0:
        return f"{mins} MIN"
    return "<1 MIN"
