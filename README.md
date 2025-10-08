# ETL & DATA MODELING

**Title**: Sales Data Transformation for Analytical Reporting

This project implements a complete ETL pipeline for sales data transformation, featuring a **star schema** data warehouse design in SQLite. The solution processes transactional sales data and builds analytical-ready tables to answer key business questions.

> **Key Business Question**: "What is the total revenue for each product category for each month in the data?"

---

## PROJECT STRUCTURE

```
tis-assessment/
├── .gitignore             # Git ignore file to exclude generated files
├── data/
│   ├── orders.csv          # Raw sales transaction data
│   └── products.csv        # Product master data
├── etl/
│   └── etl.py             # Main ETL pipeline script 
├── sql/
│   └── queries.sql        # Business analytics SQL queries (In this case, the query is for the above key business question)
├── run_query.py           # Script to execute SQL queries 
├── view_db.py             # Allows user to view full database for debugging purposes
├── requirements.txt       # Python dependencies
└── README.md              # Overview 
```

**Note**: `warehouse.db` is generated when you run `python etl/etl.py` and is excluded from Git via `.gitignore`.

---

## QUICK START

### Prerequisites
- Python 3.8+ 
- Git

### Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/jangleloom/tis-assessment
cd tis-assessment

# 2. Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the complete ETL pipeline
python etl/etl.py

# 5. Execute business analytics query
python run_query.py

# 6. (Optional) Inspect database contents, can be used for debugging purposes
python view_db.py
```

---

## DATA MODEL DESIGN (TASK 2)

### Star Schema Architecture

The solution implements a **star schema** optimized for analytical querying with one fact table and two dimension tables:

#### **FactSales** (Fact Table)
- **Purpose**: Central fact table storing sales transactions
- **Grain**: One row per order line item
- **Columns**:
  - `OrderID` (VARCHAR) - Business key for the order
  - `CustomerID` (VARCHAR) - Customer identifier
  - `ProductID` (VARCHAR) - Foreign key to DimProduct
  - `DateKey` (INTEGER) - Foreign key to DimDate (YYYYMMDD format)
  - `Quantity` (INTEGER) - Number of items sold
  - `Price` (REAL) - Unit price
  - `Revenue` (REAL) - **Calculated**: Quantity × Price

#### **DimProduct** (Product Dimension)
- **Purpose**: Product master data for enriching sales facts
- **Columns**:
  - `ProductID` (VARCHAR) - Primary key
  - `ProductName` (VARCHAR) - Product display name
  - `Category` (VARCHAR) - Product category for grouping
  - `Cost` (REAL) - Product cost

#### **DimDate** (Date Dimension)
- **Purpose**: Date attributes for time-based analysis
- **Columns**:
  - `DateKey` (INTEGER) - Primary key (YYYYMMDD format)
  - `OrderDate` (DATE) - Full date value
  - `Year` (INTEGER) - Year for yearly analysis
  - `Month` (INTEGER) - Month for monthly analysis  
  - `Day` (INTEGER) - Day for daily analysis

### Relationships
- `FactSales.ProductID` → `DimProduct.ProductID` (Many-to-One) 
- `FactSales.DateKey` → `DimDate.DateKey` (Many-to-One)

---

## ETL PIPELINE IMPLEMENTATION (TASK 1)

### Extract
- Reads raw data from `orders.csv` and `products.csv`
- Validates file existence and data quality
- Returns pandas DataFrames for processing

### Transform
- **Revenue Calculation**: `Revenue = Quantity × Price`
- **Date Processing**: Derives `DateKey` (YYYYMMDD), `Year`, `Month`, `Day` from `OrderDate`
- **Data Quality**: Removes records with missing values or invalid business rules (Quantity ≤ 0, Price ≤ 0)
- **Dimension Creation**: Builds clean dimension tables with proper deduplication

### Load
- Creates SQLite database (`warehouse.db`)
- Loads transformed data into star schema tables
- Uses `if_exists="replace"` for idempotent pipeline execution

---

## SQL QUERY FOR ANALYSIS (TASK 3)

### Business Question
**"What is the total revenue for each product category for each month in the data?"**

### SQL Query
```sql
SELECT 
    d.Year,
    d.Month,
    p.Category,
    SUM(f.Revenue) AS TotalRevenue
FROM FactSales f
JOIN DimDate d ON f.DateKey = d.DateKey
JOIN DimProduct p ON f.ProductID = p.ProductID
GROUP BY d.Year, d.Month, p.Category
ORDER BY d.Year, d.Month, p.Category;
```

### Sample Results
```
Year  Month     Category    TotalRevenue
2024    1       Displays         50.00
2024    1       Peripherals     288.00
```

**Execution**: Run `python run_query.py` to execute this query against the data warehouse.

---

## DASHBOARD USE (TASK 4)

### Data Model Suitability for Dashboarding

The star schema design is **optimal for dashboard performance** because:

1. **Denormalized Structure**: Minimizes joins required for common queries
2. **Pre-calculated Metrics**: Revenue is computed during ETL, not at query time
3. **Intuitive Relationships**: Simple dimension-to-fact relationships
4. **Aggregation-Friendly**: Dimension attributes (Category, Year, Month) support GROUP BY operations
5. **Scalable**: Can easily add new dimensions without needing to restructure 

### Additional Dashboard Metrics & Visualizations

#### 1. **Top Products Dashboard** (Table)
- **Metric**: Revenue, quantity sold, and average order value by individual product
- **Business Value**: Identifies best-performing products, could be used to aid both inventory and marketing decisions
- **Implementation**: Join all tables, aggregate by ProductName, calculate AVG(Revenue) per transaction

#### 2. **Category Performance Matrix** (Bar Chart)
- **Metric**: Total revenue and transaction count by product category
- **Business Value**: Shows which categories generates the most revenue and customer engagement
- **Implementation**: Aggregate FactSales.Revenue and COUNT(*) grouped by DimProduct.Category

#### 3. **Revenue Trend Analysis** (Line Chart)
- **Metric**: Monthly revenue over time by product category
- **Business Value**: Identifies seasonal patterns, growth trends, and category performance
- **Implementation**: Use DimDate.Month/Year with FactSales.Revenue grouped by DimProduct.Category

### Dashboard Performance Optimization
- Pre-aggregate common metrics (monthly totals, category summaries)
- Create indexes on foreign keys (DateKey, ProductID) for faster joins 

---

## TECHNICAL IMPLEMENTATION NOTES

### Architecture Decisions
- **SQLite Database**: Chosen for simplicity and portability; easily upgradeable to PostgreSQL/MySQL
- **Pandas for ETL**: Efficient data manipulation with built-in data quality features
- **Star Schema**: Optimizes for analytical queries over transactional performance
- **Integer DateKey**: YYYYMMDD format enables quick and efficient date range queries and partitioning

### Data Quality & Error Handling

- Ensures all required columns are present
- Removes nulls from critical fields
- Filters out invalid transactions (e.g., negative quantity or price)
- Logs errors comprehensively and rolls back transactions on failure  
    *(See error handling in `etl/etl.py`, especially in the `load()` function and exception blocks)*

### Code Quality Features
- Modular function design (separate Extract, Transform, Load functions)
- Comprehensive commenting and documentation
- Input validation and error handling
- Idempotent pipeline execution
- Testing framework with sample data validation 

---

## DEPENDENCIES

```txt
pandas>=1.5.0
sqlite3 (included with Python)
```

---

## TESTING AND VALIDATION

Run the complete pipeline and validate results:
```bash
# Execute ETL pipeline with built-in testing
python etl/etl.py

# Verify data warehouse contents
python view_db.py

# Test business analytics query
python run_query.py
```

Expected output: Data warehouse with 7 sales transactions, 4 products, and 5 unique dates, generating $338.00 total revenue across Peripherals and Displays categories.

---

## SUPPORT

For questions or issues with this assessment submission, please refer to the code comments or examine the modular function implementations in `etl/etl.py`.
