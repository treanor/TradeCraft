import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# Connect to database
conn = sqlite3.connect('data/tradecraft.db')

# Check date range and account distribution
query = '''
SELECT 
    account_id,
    DATE(opened_at) as trade_date,
    COUNT(*) as trades_count,
    MIN(opened_at) as earliest_trade,
    MAX(opened_at) as latest_trade
FROM trades
GROUP BY account_id, DATE(opened_at)
ORDER BY account_id, trade_date
'''

df = pd.read_sql_query(query, conn)
print('Trade distribution by account and date:')
print(df.to_string())

# Check overall stats
overall_query = '''
SELECT 
    account_id,
    COUNT(*) as total_trades,
    MIN(opened_at) as earliest_trade,
    MAX(opened_at) as latest_trade,
    COUNT(DISTINCT DATE(opened_at)) as unique_days
FROM trades
GROUP BY account_id
'''

overall_df = pd.read_sql_query(overall_query, conn)
print('\n\nOverall stats by account:')
print(overall_df.to_string())

# Calculate date range
three_months_ago = datetime.now() - timedelta(days=90)
print(f'\n\nThree months ago from today: {three_months_ago.strftime("%Y-%m-%d")}')
print(f'Today: {datetime.now().strftime("%Y-%m-%d")}')

conn.close()
