import sqlite3

conn = sqlite3.connect("data/enterprise.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY, month TEXT, region TEXT, revenue REAL
)
""")
conn.execute("INSERT INTO sales (month, region, revenue) VALUES ('Jan', 'West', 12000)")
conn.execute("INSERT INTO sales (month, region, revenue) VALUES ('Feb', 'West', 15000)")
conn.execute("INSERT INTO sales (month, region, revenue) VALUES ('Jan', 'East', 9000)")
conn.commit()
conn.close()
print("Database seeded.")