import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('warehouse.db')

# Read and execute your SQL query
with open('sql/queries.sql', 'r') as file:
    query = file.read()

print("=== Business Question ===")
print("What is the total revenue for each product category for each month in the data?")
print("\n=== SQL Query ===")
print(query)

print("\n=== Query Results ===")
results = pd.read_sql_query(query, conn)
print(results)

print(f"\n=== Summary ===")
print(f"Total rows returned: {len(results)}")
print(f"Total revenue across all categories: ${results['TotalRevenue'].sum():.2f}")

conn.close()