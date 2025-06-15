import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('data/tradecraft.db')

# Check tags data
query = """
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN tags IS NOT NULL AND tags != '' THEN 1 ELSE 0 END) as trades_with_tags
FROM trades
"""

result = pd.read_sql_query(query, conn)
print("Database Stats:")
print(result)

# Get sample tags
sample_query = "SELECT tags FROM trades WHERE tags IS NOT NULL AND tags != '' LIMIT 10"
sample_tags = pd.read_sql_query(sample_query, conn)
print("\nSample tags:")
print(sample_tags)

conn.close()
