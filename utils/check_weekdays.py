import sqlite3

con = sqlite3.connect('data/tradecraft.db')
cur = con.cursor()
print('weekday n')
rows = list(cur.execute("SELECT strftime('%w', opened_at) as weekday, COUNT(*) as n FROM trades GROUP BY weekday ORDER BY weekday;"))
for row in rows:
    print(f'{row[0]} {row[1]}')
print('Total trades:', cur.execute('SELECT COUNT(*) FROM trades').fetchone()[0])
print('Sample opened_at values:')
for row in cur.execute("SELECT opened_at FROM trades ORDER BY opened_at LIMIT 5;"):
    print(row[0])
con.close()
