import sqlite3
import pandas as pd
from .config import DB_PATH, OUTPUTS


def connect():
    return sqlite3.connect(DB_PATH)


QUERIES = {
    'monthly_sales': '''
        SELECT d.year, d.month, d.month_name,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               SUM(f.quantity) AS units
        FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    ''',
    'category_sales': '''
        SELECT p.category,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               ROUND(SUM(f.profit), 2) AS profit,
               SUM(f.quantity) AS units
        FROM fact_sales f JOIN dim_product p ON p.product_key=f.product_key
        GROUP BY p.category ORDER BY revenue DESC
    ''',
    'region_sales': '''
        SELECT l.region, l.state, l.city,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               SUM(f.quantity) AS units
        FROM fact_sales f JOIN dim_location l ON l.location_key=f.location_key
        GROUP BY l.region, l.state, l.city
        ORDER BY revenue DESC
    ''',
    'product_sales': '''
        SELECT p.product_id, p.product_name, p.category,
               ROUND(SUM(f.sales_amount), 2) AS revenue,
               SUM(f.quantity) AS units,
               ROUND(SUM(f.profit), 2) AS profit
        FROM fact_sales f JOIN dim_product p ON p.product_key=f.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC
    ''',
    'customer_rfm': '''
        WITH x AS (
            SELECT f.customer_key,
                   MAX(d.full_date) AS last_purchase,
                   COUNT(DISTINCT f.order_id) AS frequency,
                   SUM(f.sales_amount) AS monetary
            FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
            GROUP BY f.customer_key
        ), anchor AS (SELECT MAX(full_date) AS max_date FROM dim_date)
        SELECT c.customer_id, c.name, x.last_purchase,
               CAST(julianday(anchor.max_date)-julianday(x.last_purchase) AS INTEGER) AS recency,
               x.frequency, ROUND(x.monetary, 2) AS monetary,
               c.city, c.state
        FROM x JOIN dim_customer c ON c.customer_key=x.customer_key
        CROSS JOIN anchor
        ORDER BY monetary DESC
    ''',
}


def export():
    with connect() as conn:
        for name, q in QUERIES.items():
            pd.read_sql_query(q, conn).to_csv(OUTPUTS / f'{name}.csv', index=False)
    print('OLAP exports complete.')


if __name__ == '__main__':
    export()
