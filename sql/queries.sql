/* 
SQL query to get total sales revenue per product category per month
Joining FactSales with DimDate and DimProduct to get the necessary detail
*/
SELECT 
    d.Year,
    d.Month,
    p.Category,
    SUM(f.Revenue) AS TotalRevenue
FROM FactSales f
JOIN DimDate d ON f.DateKey = d.DateKey -- join if FactSales.DateKey matches DimDate.DateKey
JOIN DimProduct p ON f.ProductID = p.ProductID -- join if FactSales.ProductID matches DimProduct.ProductID
GROUP BY d.Year, d.Month, p.Category 
ORDER BY d.Year, d.Month, p.Category;