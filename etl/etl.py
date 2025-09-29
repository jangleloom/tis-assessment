import pandas as pd
import sqlite3

# ===== EXTRACT =====
# Extract -- read data from orders.csv and products.csv
def extract(orders_file, products_file):
    orders = pd.read_csv(orders_file)
    products = pd.read_csv(products_file)

    print(f"Orders shape: {orders.shape}")
    print(f"Products shape: {products.shape}")
    print("Data extraction completed")

    return orders, products

# ===== TRANSFORM =====
# Transform -- DimDate, DimProduct, FactSales tables

# Create DimDate ie. Dimension table so that facts/transactions can be analyzed by date
# Filters: year, month, day 
# Fetch using YYYYYMMDD is an int key for joining with fact table
def transform_date(orders):
    orders["OrderDate"] = pd.to_datetime(orders["OrderDate"]) # Convert to datetime
    dim_date = orders[["OrderDate"]].drop_duplicates().copy() # Keep only one row for each date 

    # Add attributes
    dim_date["DateKey"] = dim_date["OrderDate"].dt.strftime("%Y%m%d").astype(int) # Create DateKey 
    dim_date["Year"] = dim_date["OrderDate"].dt.year
    dim_date["Month"] = dim_date["OrderDate"].dt.month
    dim_date["Day"] = dim_date["OrderDate"].dt.day
    
    # Reorder columns
    dim_date = dim_date[["DateKey", "OrderDate", "Year", "Month", "Day"]]
    return dim_date

# Create DimProduct ie. Dimension table for products
# Select only relevant columns for analysis from products data
def transform_product(products):
    # # Select data columns needed for DimProduct
    dim_product = products.copy() # Create a safe copy to avoid modifying original DataFrame
    dim_product = dim_product[["ProductID", "ProductName", "Category", "Cost"]] 
    return dim_product

# Create FactSales ie. Fact table for sales transactions
# Calculate Revenue as Quantity * Price
def transform_fact_sales(orders):
    fact_sales = orders.copy()

    # Drop rows with missing values in critical columns
    fact_sales = fact_sales.dropna(subset=["OrderID", "CustomerID", "ProductID", "OrderDate", "Quantity", "Price"])

    # Drop if quantity <= 0 or price <= 0
    fact_sales = fact_sales[(fact_sales["Quantity"] > 0) & (fact_sales["Price"] > 0)]
    
    # Calculate Revenue 
    fact_sales["Revenue"] = fact_sales["Quantity"] * fact_sales["Price"]

    # Add DateKey for joining with DimDate
    fact_sales["OrderDate"] = pd.to_datetime(fact_sales["OrderDate"]) # Convert to datetime
    fact_sales["DateKey"] = fact_sales["OrderDate"].dt.strftime("%Y%m%d").astype(int) # Create DateKey  

    # Select columns needed for fact table and in order
    fact_sales = fact_sales[["OrderID", "CustomerID", "ProductID", "DateKey", "Quantity", "Price", "Revenue"]]

    return fact_sales

# ===== LOAD =====
# Load -- load the transformed data into a SQLite database
def load(dim_date, dim_product, fact_sales, db_file):
    # create a new SQLite database (or connect to existing)
    conn = sqlite3.connect(db_file)

    # Save each dataframe as a table    
    dim_date.to_sql("DimDate", conn, if_exists="replace", index=False)
    dim_product.to_sql("DimProduct", conn, if_exists="replace", index=False)
    fact_sales.to_sql("FactSales", conn, if_exists="replace", index=False)
    
    # Close connection
    conn.close()
    print("Data loaded into SQLite database")


if __name__ == "__main__":
    print("=== Testing Extract Function ===")
    try:
        orders, products = extract("data/orders.csv", "data/products.csv")
        
        print("\n=== Orders Data ===")
        print(f"Columns: {list(orders.columns)}")
        print(orders.head())
        
        print("\n=== Products Data ===")
        print(f"Columns: {list(products.columns)}")
        print(products.head())
        
        print("\n=== Testing Transform Functions ===")
        dim_date = transform_date(orders)
        print(f"\nDimDate shape: {dim_date.shape}")
        print(dim_date.head())
        
        dim_product = transform_product(products)
        print(f"\nDimProduct shape: {dim_product.shape}")
        print(dim_product.head())

        fact_sales = transform_fact_sales(orders)
        print(f"\nFactSales shape: {fact_sales.shape}")
        print(fact_sales.head())

        print("\n=== Testing Load Function ===")
        load(dim_date, dim_product, fact_sales, "warehouse.db")
        
        print("\n=== All tests successful ===")

    except Exception as e:
        print(f"Error: {e}")
