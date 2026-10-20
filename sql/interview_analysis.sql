-- Interview-ready analytical SQL examples (SQLite compatible).
-- Grain note: fact_sales is at order-item/product sales-row grain, not one row per order.

-- 1) Monthly revenue, profit and month-over-month revenue change.
WITH monthly AS (
    SELECT d.year, d.month,
           SUM(f.sales_amount) AS revenue,
           SUM(f.profit) AS profit
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
), compared AS (
    SELECT *, LAG(revenue) OVER (ORDER BY year, month) AS previous_month_revenue
    FROM monthly
)
SELECT year, month, ROUND(revenue, 2) AS revenue, ROUND(profit, 2) AS profit,
       ROUND(100.0 * (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0), 2) AS revenue_mom_pct
FROM compared ORDER BY year, month;

-- 2) Top 10 products by revenue, with profit margin.
SELECT p.product_name, p.category,
       ROUND(SUM(f.sales_amount), 2) AS revenue,
       ROUND(SUM(f.profit), 2) AS profit,
       ROUND(100.0 * SUM(f.profit) / NULLIF(SUM(f.sales_amount), 0), 2) AS profit_margin_pct
FROM fact_sales f JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY revenue DESC LIMIT 10;

-- 3) Customer value: frequency, monetary value and last purchase date.
SELECT c.customer_id, c.name,
       COUNT(DISTINCT f.order_id) AS order_frequency,
       ROUND(SUM(f.sales_amount), 2) AS lifetime_revenue,
       MAX(d.full_date) AS last_purchase_date
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY c.customer_key, c.customer_id, c.name
ORDER BY lifetime_revenue DESC LIMIT 20;

-- 4) Category and region performance (a useful BI slice/dice example).
SELECT p.category, l.region,
       ROUND(SUM(f.sales_amount), 2) AS revenue,
       ROUND(SUM(f.profit), 2) AS profit,
       COUNT(DISTINCT f.order_id) AS orders
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_location l ON l.location_key = f.location_key
GROUP BY p.category, l.region
ORDER BY revenue DESC;

-- 5) Revenue concentration by customer (top 20% ranking is available via PERCENT_RANK).
WITH customer_revenue AS (
    SELECT c.customer_id, SUM(f.sales_amount) AS revenue
    FROM fact_sales f JOIN dim_customer c ON c.customer_key = f.customer_key
    GROUP BY c.customer_key, c.customer_id
), ranked AS (
    SELECT *, PERCENT_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank_pct
    FROM customer_revenue
)
SELECT customer_id, ROUND(revenue, 2) AS revenue,
       ROUND(revenue_rank_pct * 100, 1) AS rank_percentile
FROM ranked ORDER BY revenue DESC LIMIT 25;
