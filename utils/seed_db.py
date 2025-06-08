"""
Seed the TradeCraft database with sample data for development and testing.
This script adds trades using the Trade objects from sample_data.
"""
from datetime import datetime
from typing import List
from utils import db_utils
from models import Trade


def seed_database(trades: List[Trade]) -> None:
    """
    Seed the database with a list of Trade objects.
    
    Args:
        trades: List of Trade objects to insert into the database
    """
    try:
        # Get or create default user
        users = db_utils.get_users()
        if users:
            user_id = users[0]['id']
        else:
            user_id = db_utils.add_user("default_user", "user@tradecraft.com")
        
        for trade in trades:
            # Add the trade
            trade_id = db_utils.add_trade(
                user_id=user_id,
                symbol=trade.symbol,
                asset_type=trade.asset_type.value,
                status=trade.status,
                created_at=trade.created_at.isoformat(),
                journal_entry=trade.journal_entry
            )
            
            # Add trade legs
            for leg in trade.legs:
                db_utils.add_trade_leg(
                    trade_id=trade_id,
                    action=leg.action.value,
                    datetime=leg.datetime.isoformat(),
                    quantity=leg.quantity,
                    price=leg.price,
                    fee=leg.fee
                )
              # Add tags
            for tag in trade.tags:
                db_utils.add_tag(trade_id, tag)
        
        print(f"Seeded {len(trades)} trades into the database.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    from sample_data import sample_trades
    seed_database(sample_trades)
