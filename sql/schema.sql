PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_payment;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL UNIQUE,
    name TEXT,
    gender TEXT,
    age INTEGER,
    age_group TEXT,
    city TEXT,
    state TEXT,
    region TEXT
);

CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL UNIQUE,
    product_name TEXT,
    brand TEXT,
    category TEXT,
    sub_category TEXT,
    unit_price REAL,
    unit_cost REAL
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    day INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    year INTEGER,
    week INTEGER
);

CREATE TABLE dim_location (
    location_key INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT DEFAULT 'India',
    region TEXT,
    UNIQUE(city, state)
);

CREATE TABLE dim_payment (
    payment_key INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_method TEXT NOT NULL UNIQUE
);

CREATE TABLE fact_sales (
    sales_key INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    order_item_id TEXT NOT NULL,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    location_key INTEGER NOT NULL,
    payment_key INTEGER,
    quantity INTEGER,
    unit_price REAL,
    discount REAL,
    gross_sales REAL,
    sales_amount REAL,
    cost_amount REAL,
    profit REAL,
    returned INTEGER DEFAULT 0,
    FOREIGN KEY(date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY(customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY(product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY(location_key) REFERENCES dim_location(location_key),
    FOREIGN KEY(payment_key) REFERENCES dim_payment(payment_key)
);

CREATE INDEX idx_fact_date ON fact_sales(date_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_product ON fact_sales(product_key);
CREATE INDEX idx_fact_order ON fact_sales(order_id);
