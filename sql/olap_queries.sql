-- SQLite-compatible OLAP demonstrations.

-- ROLL-UP: day -> month -> quarter -> year (implemented as separate aggregation levels)
SELECT d.year, d.quarter, d.month, ROUND(SUM(f.sales_amount),2) AS revenue
FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
GROUP BY d.year, d.quarter, d.month
ORDER BY d.year, d.quarter, d.month;

-- DRILL-DOWN: year -> quarter -> month -> day
SELECT d.year, d.quarter, d.month, d.day, ROUND(SUM(f.sales_amount),2) AS revenue
FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
GROUP BY d.year, d.quarter, d.month, d.day
ORDER BY d.year, d.quarter, d.month, d.day;

-- SLICE: only 2026
SELECT d.year, p.category, ROUND(SUM(f.sales_amount),2) AS revenue
FROM fact_sales f
JOIN dim_date d ON d.date_key=f.date_key
JOIN dim_product p ON p.product_key=f.product_key
WHERE d.year=2026
GROUP BY d.year, p.category
ORDER BY revenue DESC;

-- DICE: Electronics in South region during Q2 2026
SELECT d.year, d.quarter, p.category, l.region, ROUND(SUM(f.sales_amount),2) AS revenue
FROM fact_sales f
JOIN dim_date d ON d.date_key=f.date_key
JOIN dim_product p ON p.product_key=f.product_key
JOIN dim_location l ON l.location_key=f.location_key
WHERE d.year=2026 AND d.quarter=2
  AND p.category='Electronics' AND l.region='South'
GROUP BY d.year, d.quarter, p.category, l.region;

-- PIVOT: category x year
SELECT p.category,
       ROUND(SUM(CASE WHEN d.year=2025 THEN f.sales_amount ELSE 0 END),2) AS y2025,
       ROUND(SUM(CASE WHEN d.year=2026 THEN f.sales_amount ELSE 0 END),2) AS y2026
FROM fact_sales f
JOIN dim_product p ON p.product_key=f.product_key
JOIN dim_date d ON d.date_key=f.date_key
GROUP BY p.category ORDER BY p.category;
