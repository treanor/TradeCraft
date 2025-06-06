from models import Trade, TradeLeg, AssetType, TradeAction
from datetime import datetime, timedelta
import random

# Helper to generate random sample trades for 3 months
symbols = ["AAPL", "MSFT", "TSLA", "SPY", "QQQ", "GOOG", "AMZN", "NVDA", "META", "AMD"]
option_suffixes = ["C", "P"]
statuses = ["WIN", "LOSS", "OPEN"]

weeks = 52
start_date = datetime.now() - timedelta(weeks=weeks)
trades_per_day = 5

def random_option_symbol():
    base = random.choice(symbols)
    exp = f"25{random.randint(3, 6):02d}{random.randint(1,28):02d}"
    strike = random.randint(50, 600)
    cp = random.choice(option_suffixes)
    return f"{base}{exp}{cp}{strike}"

def random_trade(trade_id, date):
    symbol = random_option_symbol()
    status = random.choice(statuses)
    entry_price = round(random.uniform(50, 500), 2)
    qty = random.randint(1, 5)
    # Generate random entry time between 9:30 and 16:00
    entry_hour = random.randint(9, 15)
    if entry_hour == 9:
        entry_minute = random.randint(30, 59)
    else:
        entry_minute = random.randint(0, 59)
    entry_date = date.replace(hour=entry_hour, minute=entry_minute, second=0, microsecond=0)
    hold_days = random.randint(0, 5)
    if status == "OPEN":
        exit_date = entry_date
    else:
        # For closed trades, exit is after hold_days, random time between entry and 16:00
        exit_base_date = entry_date + timedelta(days=hold_days)
        exit_hour = random.randint(entry_hour if hold_days == 0 else 9, 15)
        if exit_hour == 9:
            exit_minute = random.randint(30, 59)
        else:
            exit_minute = random.randint(0, 59)
        exit_date = exit_base_date.replace(hour=exit_hour, minute=exit_minute, second=0, microsecond=0)
    # Ensure PnL matches status
    if status == "WIN":
        exit_price = entry_price + abs(round(random.uniform(1, 100), 2))
    elif status == "LOSS":
        exit_price = entry_price - abs(round(random.uniform(1, 100), 2))
    else:  # OPEN
        exit_price = entry_price + round(random.uniform(-50, 100), 2)
    # --- Add random tags ---
    tag_pool = ["Fidelity", "TastyTrade", "qqq", "SPY", "--NO TAGS--"]
    tags = []
    if random.random() < 0.7:
        tags.append(random.choice(tag_pool[:-1]))
    if random.random() < 0.2:
        tags.append(random.choice(tag_pool[:-1]))
    if not tags:
        tags = [tag_pool[-1]]
    legs = [
        TradeLeg(action=TradeAction.BUY, datetime=entry_date, quantity=qty, price=entry_price),
    ]
    if status != "OPEN":
        legs.append(TradeLeg(action=TradeAction.SELL, datetime=exit_date, quantity=qty, price=exit_price))
    return Trade(
        trade_id=str(trade_id),
        user_id="user1",
        symbol=symbol,
        asset_type=AssetType.OPTION,
        created_at=entry_date,
        status=status,
        legs=legs,
        tags=tags
    )

# Sample trades for development/demo
sample_trades = []
trade_id = 1
for week in range(weeks):
    week_start = start_date + timedelta(weeks=week)
    for i in range(7):  # 7 days per week
        trade_date = week_start + timedelta(days=i)
        if trade_date.weekday() < 5:  # Only Monday (0) to Friday (4)
            for j in range(trades_per_day):
                sample_trades.append(random_trade(trade_id, trade_date))
                trade_id += 1
