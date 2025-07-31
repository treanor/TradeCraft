import sqlite3
import random

# Connect to database
conn = sqlite3.connect('data/tradecraft.db')
cursor = conn.cursor()

# Sample tags to add
sample_tags = [
    'day-trade', 'swing-trade', 'earnings-play', 'momentum', 'reversal',
    'breakout', 'pullback', 'gap-up', 'gap-down', 'support-bounce',
    'resistance-break', 'trend-following', 'contrarian', 'scalp', 'position'
]

# Get first 50 trades to add tags to
cursor.execute("SELECT id FROM trades LIMIT 50")
trade_ids = [row[0] for row in cursor.fetchall()]

# Add random tags to trades
for trade_id in trade_ids:
    # Random number of tags (1-3 per trade)
    num_tags = random.randint(1, 3)
    selected_tags = random.sample(sample_tags, num_tags)
    tags_string = ', '.join(selected_tags)
    
    cursor.execute("UPDATE trades SET tags = ? WHERE id = ?", (tags_string, trade_id))

# Commit changes
conn.commit()

# Verify the update
cursor.execute("SELECT COUNT(*) FROM trades WHERE tags IS NOT NULL AND tags != ''")
tagged_count = cursor.fetchone()[0]
print(f"Successfully added tags to {tagged_count} trades")

# Show sample tagged trades
cursor.execute("SELECT id, asset_symbol, tags FROM trades WHERE tags IS NOT NULL AND tags != '' LIMIT 10")
sample_trades = cursor.fetchall()
print("\nSample tagged trades:")
for trade in sample_trades:
    print(f"Trade {trade[0]} ({trade[1]}): {trade[2]}")

conn.close()
