import sqlite3
from pathlib import Path
import pandas as pd
from .config import RAW, DB_PATH, ROOT


def age_group(a):
    return '18-25' if a <= 25 else '26-35' if a <= 35 else '36-45' if a <= 45 else '46-55' if a <= 55 else '56+'


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def load():
    c = pd.read_csv(RAW / 'customers.csv')
    p = pd.read_csv(RAW / 'products.csv')
    o = pd.read_csv(RAW / 'orders.csv', parse_dates=['order_date'])
    oi = pd.read_csv(RAW / 'order_items.csv')
    pay = pd.read_csv(RAW / 'payments.csv')
    ret = pd.read_csv(RAW / 'returns.csv', parse_dates=['return_date'])

    c['age_group'] = c['age'].map(age_group)
    o = o[o['status'].eq('Completed')].copy()

    oi = (
        oi.merge(o[['order_id', 'customer_id', 'order_date']], on='order_id', how='inner')
          .merge(c[['customer_id', 'city', 'state', 'region']], on='customer_id', how='left')
          .merge(p[['product_id', 'unit_cost']], on='product_id', how='left')
    )
    oi['gross_sales'] = oi['quantity'] * oi['unit_price']
    oi['sales_amount'] = oi['gross_sales'] * (1 - oi['discount'])
    oi['cost_amount'] = oi['quantity'] * oi['unit_cost']
    oi['profit'] = oi['sales_amount'] - oi['cost_amount']
    oi['returned'] = oi['order_id'].isin(ret['order_id']).astype(int)

    conn = connect()
    try:
        schema = (ROOT / 'sql' / 'schema.sql').read_text(encoding='utf-8')
        conn.executescript(schema)

        conn.executemany(
            '''INSERT INTO dim_customer
               (customer_id,name,gender,age,age_group,city,state,region)
               VALUES (?,?,?,?,?,?,?,?)''',
            c[['customer_id','name','gender','age','age_group','city','state','region']].itertuples(index=False, name=None)
        )

        conn.executemany(
            '''INSERT INTO dim_product
               (product_id,product_name,brand,category,sub_category,unit_price,unit_cost)
               VALUES (?,?,?,?,?,?,?)''',
            p[['product_id','product_name','brand','category','sub_category','unit_price','unit_cost']].itertuples(index=False, name=None)
        )

        dates = pd.date_range(o['order_date'].min(), o['order_date'].max(), freq='D')
        date_rows = []
        for d in dates:
            date_rows.append((
                int(d.strftime('%Y%m%d')), d.strftime('%Y-%m-%d'), d.day, d.month,
                d.strftime('%B'), (d.month - 1) // 3 + 1, d.year, int(d.isocalendar().week)
            ))
        conn.executemany(
            '''INSERT INTO dim_date
               (date_key,full_date,day,month,month_name,quarter,year,week)
               VALUES (?,?,?,?,?,?,?,?)''', date_rows
        )

        loc = c[['city','state','region']].drop_duplicates()
        conn.executemany(
            'INSERT INTO dim_location(city,state,region) VALUES (?,?,?)',
            loc.itertuples(index=False, name=None)
        )

        methods = [(m,) for m in sorted(pay['payment_method'].dropna().unique())]
        conn.executemany('INSERT INTO dim_payment(payment_method) VALUES (?)', methods)

        customers = dict(conn.execute('SELECT customer_id, customer_key FROM dim_customer').fetchall())
        products = dict(conn.execute('SELECT product_id, product_key FROM dim_product').fetchall())
        locations = dict(conn.execute('SELECT city || \'|\' || state, location_key FROM dim_location').fetchall())
        payments = dict(conn.execute('SELECT payment_method, payment_key FROM dim_payment').fetchall())

        order_payment = dict(pay[['order_id','payment_method']].itertuples(index=False, name=None))
        fact_rows = []
        for r in oi.itertuples(index=False):
            method = order_payment.get(r.order_id, 'Unknown')
            fact_rows.append((
                r.order_id, r.order_item_id, int(pd.Timestamp(r.order_date).strftime('%Y%m%d')),
                customers[r.customer_id], products[r.product_id],
                locations[f'{r.city}|{r.state}'], payments.get(method),
                int(r.quantity), float(r.unit_price), float(r.discount),
                float(r.gross_sales), float(r.sales_amount), float(r.cost_amount),
                float(r.profit), int(r.returned)
            ))

        conn.executemany(
            '''INSERT INTO fact_sales
               (order_id,order_item_id,date_key,customer_key,product_key,location_key,
                payment_key,quantity,unit_price,discount,gross_sales,sales_amount,
                cost_amount,profit,returned)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            fact_rows
        )
        conn.commit()

        counts = {
            'customers': conn.execute('SELECT COUNT(*) FROM dim_customer').fetchone()[0],
            'products': conn.execute('SELECT COUNT(*) FROM dim_product').fetchone()[0],
            'dates': conn.execute('SELECT COUNT(*) FROM dim_date').fetchone()[0],
            'locations': conn.execute('SELECT COUNT(*) FROM dim_location').fetchone()[0],
            'payments': conn.execute('SELECT COUNT(*) FROM dim_payment').fetchone()[0],
            'sales_rows': conn.execute('SELECT COUNT(*) FROM fact_sales').fetchone()[0],
        }
        print('SQLite ETL load complete:', counts)
    finally:
        conn.close()


if __name__ == '__main__':
    load()
