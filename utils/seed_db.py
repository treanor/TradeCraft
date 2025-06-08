"""
Seed the TradeCraft database with sample data for development and testing.
This script adds a sample user, trades, trade legs, and tags.
"""
from datetime import datetime
from utils import db_utils

def seed():
    # Add a sample user
    user_id = db_utils.add_user("sampleuser", "sampleuser@example.com")

    # Add 5 sample trades
    trades = [
        {
            "symbol": "AAPL",
            "asset_type": "stock",
            "status": "WIN",
            "created_at": datetime(2024, 6, 1, 9, 30).isoformat(),
            "journal_entry": "Bought on breakout, sold into strength.",
            "legs": [
                {"action": "buy", "datetime": datetime(2024, 6, 1, 9, 31).isoformat(), "quantity": 10, "price": 180.00, "fee": 1.00},
                {"action": "sell", "datetime": datetime(2024, 6, 1, 15, 55).isoformat(), "quantity": 10, "price": 185.00, "fee": 1.00}
            ],
            "tags": ["breakout", "momentum"]
        },
        {
            "symbol": "TSLA",
            "asset_type": "stock",
            "status": "LOSS",
            "created_at": datetime(2024, 6, 2, 10, 0).isoformat(),
            "journal_entry": "Tried to catch a reversal, stopped out.",
            "legs": [
                {"action": "buy", "datetime": datetime(2024, 6, 2, 10, 5).isoformat(), "quantity": 5, "price": 600.00, "fee": 1.00},
                {"action": "sell", "datetime": datetime(2024, 6, 2, 14, 30).isoformat(), "quantity": 5, "price": 590.00, "fee": 1.00}
            ],
            "tags": ["reversal", "stopout"]
        },
        {
            "symbol": "MSFT",
            "asset_type": "stock",
            "status": "OPEN",
            "created_at": datetime(2024, 6, 3, 11, 0).isoformat(),
            "journal_entry": "Swing trade, holding for earnings.",
            "legs": [
                {"action": "buy", "datetime": datetime(2024, 6, 3, 11, 10).isoformat(), "quantity": 15, "price": 300.00, "fee": 1.00}
            ],
            "tags": ["swing", "earnings"]
        },
        {
            "symbol": "SPY",
            "asset_type": "option",
            "status": "WIN",
            "created_at": datetime(2024, 6, 4, 9, 45).isoformat(),
            "journal_entry": "Bought calls on market rally.",
            "legs": [
                {"action": "buy_to_open", "datetime": datetime(2024, 6, 4, 9, 50).isoformat(), "quantity": 1, "price": 5.00, "fee": 0.65},
                {"action": "sell_to_close", "datetime": datetime(2024, 6, 4, 15, 45).isoformat(), "quantity": 1, "price": 7.50, "fee": 0.65}
            ],
            "tags": ["options", "call", "rally"]
        },
        {
            "symbol": "AMZN",
            "asset_type": "stock",
            "status": "WIN",
            "created_at": datetime(2024, 6, 5, 13, 0).isoformat(),
            "journal_entry": "Scalped quick move after news.",
            "legs": [
                {"action": "buy", "datetime": datetime(2024, 6, 5, 13, 5).isoformat(), "quantity": 3, "price": 3200.00, "fee": 1.00},
                {"action": "sell", "datetime": datetime(2024, 6, 5, 13, 45).isoformat(), "quantity": 3, "price": 3220.00, "fee": 1.00}
            ],
            "tags": ["scalp", "news"]
        }
    ]

    for trade in trades:
        trade_id = db_utils.add_trade(
            user_id=user_id,
            symbol=trade["symbol"],
            asset_type=trade["asset_type"],
            status=trade["status"],
            created_at=trade["created_at"],
            journal_entry=trade["journal_entry"]
        )
        for leg in trade["legs"]:
            db_utils.add_trade_leg(
                trade_id=trade_id,
                action=leg["action"],
                datetime=leg["datetime"],
                quantity=leg["quantity"],
                price=leg["price"],
                fee=leg.get("fee", 0.0)
            )
        for tag in trade["tags"]:
            db_utils.add_tag(trade_id, tag)

    print("Sample data seeded.")

if __name__ == "__main__":
    seed()
