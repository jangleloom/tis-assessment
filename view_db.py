import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data/etl_database.db')

# View all tables in the database
print("=== Tables in the database ===")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print(tables)

# View each table's content
for table_name in tables['name']:
    print(f"\n=== {table_name} Table ===")
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10;", conn)
    print(f"Shape: {df.shape}")
    print(df)
    print("-" * 50)

conn.close()