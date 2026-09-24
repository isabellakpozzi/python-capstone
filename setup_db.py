import sqlite3
conn = sqlite3.connect("data/enterprise.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY, month TEXT, region TEXT, revenue REAL
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS churn (
    id INTEGER PRIMARY KEY, month TEXT, customers_start INTEGER, customers_lost INTEGER
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS employee_satisfaction (
    id INTEGER PRIMARY KEY, quarter TEXT, avg_score REAL, industry_benchmark REAL
)
""")

sales_rows = [
    ('Jan', 'West', 12000), ('Feb', 'West', 15000), ('Mar', 'West', 14000),
    ('Oct', 'West', 20000), ('Nov', 'West', 22000), ('Dec', 'West', 25000),
    ('Jan', 'East', 9000),  ('Oct', 'East', 17000), ('Nov', 'East', 18000), ('Dec', 'East', 19500),
]
conn.executemany("INSERT INTO sales (month, region, revenue) VALUES (?, ?, ?)", sales_rows)

conn.execute("ALTER TABLE sales ADD COLUMN quarter TEXT")
conn.execute("""
UPDATE sales SET quarter = CASE
    WHEN month IN ('Jan','Feb','Mar') THEN 'Q1'
    WHEN month IN ('Apr','May','Jun') THEN 'Q2'
    WHEN month IN ('Jul','Aug','Sep') THEN 'Q3'
    WHEN month IN ('Oct','Nov','Dec') THEN 'Q4'
END
""")

churn_rows = [
    ('Jan', 500, 15), ('Feb', 510, 12), ('Mar', 520, 18),
    ('Oct', 600, 20), ('Nov', 610, 14), ('Dec', 615, 10),
]
conn.executemany(
    "INSERT INTO churn (month, customers_start, customers_lost) VALUES (?, ?, ?)", churn_rows
)

satisfaction_rows = [
    ('Q1', 7.8, 7.5), ('Q2', 8.0, 7.6), ('Q3', 7.9, 7.6), ('Q4', 8.2, 7.7),
]
conn.executemany(
    "INSERT INTO employee_satisfaction (quarter, avg_score, industry_benchmark) VALUES (?, ?, ?)",
    satisfaction_rows,
)

conn.execute("""
CREATE TABLE IF NOT EXISTS quarterly_performance (
    id INTEGER PRIMARY KEY, quarter TEXT, region TEXT, revenue REAL, units_sold INTEGER
)
""")

quarterly_rows = [
    ('Q1', 'West', 41000, 410), ('Q1', 'East', 9000, 90),
    ('Q2', 'West', 45000, 450), ('Q2', 'East', 30000, 300),
    ('Q3', 'West', 48000, 480), ('Q3', 'East', 33000, 330),
    ('Q4', 'West', 67000, 670), ('Q4', 'East', 54500, 545),
]
conn.executemany(
    "INSERT INTO quarterly_performance (quarter, region, revenue, units_sold) VALUES (?, ?, ?, ?)",
    quarterly_rows,
)

conn.commit()
conn.close()
print("Database seeded.")