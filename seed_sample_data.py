#!/usr/bin/env python3
"""
Script to seed the database with sample trading data.
"""
from sample_data import sample_trades
from utils import db_utils

def seed_database(trades):
    """Seed the database with sample trades"""
    # Get or create default user
    users = db_utils.get_users()
    if users:
        user_id = users[0]['id']
    else:
        user_id = db_utils.add_user("default_user", "user@tradecraft.com")
    
    # Clear existing trades first (optional)
    print("Clearing existing trades...")
    
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

if __name__ == "__main__":
    print(f"Starting to seed {len(sample_trades)} sample trades...")
    try:
        seed_database(sample_trades)
    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    
    # Check final count
    stats = db_utils.get_trade_summary_stats()
    print(f"Total trades in database after seeding: {stats['total_trades']}")
