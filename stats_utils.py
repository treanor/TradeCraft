from models import Trade
from datetime import datetime

def get_wins(trades):
    return sum(1 for t in trades if t.status == "WIN")

def get_losses(trades):
    return sum(1 for t in trades if t.status == "LOSS")

def get_total_pnl(trades):
    pnl = 0
    for t in trades:
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl += (exit.price - entry.price) * entry.quantity
    return pnl

def filter_trades(trades, filter_key, tag_filter=None):
    import pandas as pd
    from datetime import timedelta
    now = datetime.now()
    filtered = trades
    def get_close_date(t):
        # Use the exit leg's date for closed trades, else entry leg
        if t.legs and len(t.legs) > 1:
            return t.legs[-1].datetime.date()
        elif t.legs:
            return t.legs[0].datetime.date()
        return None
    if filter_key == "all":
        filtered = trades
    elif filter_key == "today":
        filtered = [t for t in trades if get_close_date(t) == now.date()]
    elif filter_key == "yesterday":
        yest = now.date() - pd.Timedelta(days=1)
        filtered = [t for t in trades if get_close_date(t) == yest]
    elif filter_key == "this_week":
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6)
        filtered = [t for t in trades if get_close_date(t) and week_start.date() <= get_close_date(t) <= week_end.date()]
    elif filter_key == "last_week":
        week_start = now - timedelta(days=now.weekday() + 7)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6)
        filtered = [t for t in trades if get_close_date(t) and week_start.date() <= get_close_date(t) <= week_end.date()]
    elif filter_key == "this_month":
        filtered = [t for t in trades if get_close_date(t) and get_close_date(t).month == now.month and get_close_date(t).year == now.year]
    # Tag filter (intersection: trade must have at least one selected tag)
    if tag_filter:
        filtered = [t for t in filtered if any(tag in t.tags for tag in tag_filter)]
    return filtered

def get_equity_curve(trades, filter_key="all"):
    from collections import defaultdict
    import pandas as pd
    # Filter trades first, so equity curve matches the filter (like the table)
    filtered_trades = filter_trades(trades, filter_key)
    # Only include closed trades (WIN or LOSS, with both entry and exit legs)
    closed_trades = [t for t in filtered_trades if t.status.upper() in ("WIN", "LOSS") and len(t.legs) > 1]
    pnl_by_date = defaultdict(float)
    if filter_key in ("today", "yesterday"):
        # Hourly equity curve for today/yesterday
        for t in closed_trades:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            close_dt = exit.datetime.replace(minute=0, second=0, microsecond=0)
            pnl_by_date[close_dt] += pnl
        if not pnl_by_date:
            return [], []
        all_hours = pd.date_range(min(pnl_by_date.keys()), max(pnl_by_date.keys()), freq='h')
        x = []
        y = []
        equity = 0
        for h in all_hours:
            equity += pnl_by_date.get(h.to_pydatetime(), 0)
            x.append(h.strftime("%m/%d/%Y %H:00"))
            y.append(equity)
        return x, y
    else:
        # Daily equity curve for all other filters
        for t in closed_trades:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            close_date = exit.datetime.date()
            pnl_by_date[close_date] += pnl
        if not pnl_by_date:
            return [], []
        all_dates = pd.date_range(min(pnl_by_date.keys()), max(pnl_by_date.keys()), freq='D')
        x = []
        y = []
        equity = 0
        for d in all_dates:
            d_date = d.date()
            equity += pnl_by_date.get(d_date, 0)
            x.append(d_date.strftime("%m/%d/%Y"))
            y.append(equity)
        return x, y

def get_avg_win(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    if not wins:
        return 0
    return sum((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in wins) / len(wins)

def get_avg_loss(trades):
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    if not losses:
        return 0
    return sum((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in losses) / len(losses)

def get_avg_win_hold(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    if not wins:
        return 0.0
    total = sum([(t.legs[1].datetime - t.legs[0].datetime).total_seconds() for t in wins])
    avg_sec = total / len(wins)
    return avg_sec

def get_avg_loss_hold(trades):
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    if not losses:
        return 0.0
    total = sum([(t.legs[1].datetime - t.legs[0].datetime).total_seconds() for t in losses])
    avg_sec = total / len(losses)
    return avg_sec

def get_profit_factor(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    gross_win = sum((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in wins)
    gross_loss = -sum((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in losses)
    if gross_loss == 0:
        return float('inf') if gross_win > 0 else 0
    return gross_win / gross_loss

def get_expectancy(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    n = len(wins) + len(losses)
    if n == 0:
        return 0
    win_rate = len(wins) / n
    avg_win = get_avg_win(trades)
    avg_loss = get_avg_loss(trades)
    return win_rate * avg_win + (1 - win_rate) * avg_loss

def get_win_streak(trades):
    max_streak = 0
    streak = 0
    for t in trades:
        if t.status == "WIN":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def get_loss_streak(trades):
    max_streak = 0
    streak = 0
    for t in trades:
        if t.status == "LOSS":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def get_top_win(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    if not wins:
        return 0
    return max((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in wins)

def get_top_loss(trades):
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    if not losses:
        return 0
    return min((t.legs[1].price - t.legs[0].price) * t.legs[0].quantity for t in losses)

def get_avg_daily_vol(trades):
    from collections import defaultdict
    if not trades:
        return 0
    day_counts = defaultdict(int)
    for t in trades:
        if t.legs:
            day = t.legs[0].datetime.date()
            day_counts[day] += 1
    return sum(day_counts.values()) / len(day_counts) if day_counts else 0

def get_avg_size(trades):
    if not trades:
        return 0
    return sum(t.legs[0].quantity for t in trades if t.legs) / len([t for t in trades if t.legs])

def get_avg_win_pct(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    if not wins:
        return 0.0
    return sum(((t.legs[1].price - t.legs[0].price) / t.legs[0].price) * 100 for t in wins) / len(wins)

def get_avg_loss_pct(trades):
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    if not losses:
        return 0.0
    return sum(((t.legs[1].price - t.legs[0].price) / t.legs[0].price) * 100 for t in losses) / len(losses)

def get_top_win_pct(trades):
    wins = [t for t in trades if t.status == "WIN" and len(t.legs) > 1]
    if not wins:
        return 0.0
    return max(((t.legs[1].price - t.legs[0].price) / t.legs[0].price) * 100 for t in wins)

def get_top_loss_pct(trades):
    losses = [t for t in trades if t.status == "LOSS" and len(t.legs) > 1]
    if not losses:
        return 0.0
    return min(((t.legs[1].price - t.legs[0].price) / t.legs[0].price) * 100 for t in losses)

def get_performance_by_day_of_week(trades):
    # Returns dict: {day_name: total_pnl}
    import calendar
    from collections import defaultdict
    day_pnl = defaultdict(float)
    for t in trades:
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            exit_leg = t.legs[1]
            pnl = (exit_leg.price - t.legs[0].price) * t.legs[0].quantity
            day_name = calendar.day_name[exit_leg.datetime.weekday()]
            day_pnl[day_name] += pnl
    # Ensure all days present
    return {day: day_pnl.get(day, 0) for day in calendar.day_name}

def get_performance_by_hour(trades):
    # Returns dict: {hour_label: total_pnl}
    from collections import defaultdict
    hour_pnl = defaultdict(float)
    for t in trades:
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            exit_leg = t.legs[1]
            pnl = (exit_leg.price - t.legs[0].price) * t.legs[0].quantity
            hour_label = exit_leg.datetime.strftime("%I %p").lstrip("0")
            hour_pnl[hour_label] += pnl
    # Return sorted by hour (9 AM to 6 PM)
    hours = [f"{h} AM" for h in range(9, 12)] + ["12 PM"] + [f"{h} PM" for h in range(1, 7)]
    return {h: hour_pnl.get(h, 0) for h in hours}

def get_stats_by_tag(trades):
    # Returns list of dicts for DataTable, supports multiple tags per trade
    from collections import defaultdict
    tag_stats = defaultdict(lambda: {"Trades": 0, "PnL": 0.0, "PnL_pct_sum": 0.0, "Weighted_pct_num": 0.0, "Weighted_pct_den": 0.0})
    for t in trades:
        tags = getattr(t, "tags", None)
        if not tags or not isinstance(tags, list) or len(tags) == 0:
            tags = ["--NO TAGS--"]
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            notional = abs(entry.price * entry.quantity)
            pnl_pct = ((exit.price - entry.price) / entry.price) * 100 if entry.price else 0
            for tag in tags:
                tag_stats[tag]["Trades"] += 1
                tag_stats[tag]["PnL"] += pnl
                tag_stats[tag]["PnL_pct_sum"] += pnl_pct
                tag_stats[tag]["Weighted_pct_num"] += pnl_pct * notional
                tag_stats[tag]["Weighted_pct_den"] += notional
    rows = []
    for tag, stats in tag_stats.items():
        trades = stats["Trades"]
        pnl = stats["PnL"]
        pnl_pct = stats["PnL_pct_sum"] / trades if trades else 0
        weighted_pct = stats["Weighted_pct_num"] / stats["Weighted_pct_den"] if stats["Weighted_pct_den"] else 0
        rows.append({
            "Tag": tag,
            "Trades": trades,
            "PnL": f"${pnl:,.2f}",
            "PnL %": f"{pnl_pct:.2f}%",
            "Weighted %": f"{weighted_pct:.2f}%"
        })
    return rows

def get_stats_by_symbol(trades):
    from collections import defaultdict
    symbol_stats = defaultdict(lambda: {"Trades": 0, "PnL": 0.0, "PnL_pct_sum": 0.0, "Weighted_pct_num": 0.0, "Weighted_pct_den": 0.0})
    for t in trades:
        symbol = getattr(t, "symbol", "-")
        if t.status in ("WIN", "LOSS") and len(t.legs) > 1:
            entry = t.legs[0]
            exit = t.legs[1]
            pnl = (exit.price - entry.price) * entry.quantity
            notional = abs(entry.price * entry.quantity)
            pnl_pct = ((exit.price - entry.price) / entry.price) * 100 if entry.price else 0
            symbol_stats[symbol]["Trades"] += 1
            symbol_stats[symbol]["PnL"] += pnl
            symbol_stats[symbol]["PnL_pct_sum"] += pnl_pct
            symbol_stats[symbol]["Weighted_pct_num"] += pnl_pct * notional
            symbol_stats[symbol]["Weighted_pct_den"] += notional
    rows = []
    for symbol, stats in symbol_stats.items():
        trades = stats["Trades"]
        pnl = stats["PnL"]
        pnl_pct = stats["PnL_pct_sum"] / trades if trades else 0
        weighted_pct = stats["Weighted_pct_num"] / stats["Weighted_pct_den"] if stats["Weighted_pct_den"] else 0
        rows.append({
            "Symbol": symbol,
            "Trades": trades,
            "PnL": f"${pnl:,.2f}",
            "PnL %": f"{pnl_pct:.2f}%",
            "Weighted %": f"{weighted_pct:.2f}%"
        })
    return rows
