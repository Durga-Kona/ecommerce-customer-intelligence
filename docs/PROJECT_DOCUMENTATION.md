# PROJECT DOCUMENTATION
## E-Commerce Customer Intelligence & Sales Analytics Platform Using Data Warehousing and Data Mining

### Abstract
The E-Commerce Customer Intelligence & Sales Analytics Platform is an integrated Data Warehousing and Data Mining solution designed to transform raw e-commerce transaction data into actionable business intelligence. The system uses a Python/Pandas ETL pipeline to clean and integrate customer, product, order, payment and return data, stores the resulting information in a **SQLite star-schema data warehouse**, performs OLAP analysis, and applies data-mining techniques for customer segmentation, repeat-purchase classification and product association discovery. Power BI provides interactive visualization for management decision-making.

### 1. Problem Statement
E-commerce organizations generate large volumes of transactional data. Raw operational records are difficult to analyze directly because they contain different entities, granularities and business dimensions. The proposed system creates an analytical warehouse and mining layer capable of identifying sales trends, high-value customers, regional performance, purchase patterns and customer behavior.

### 2. Objectives
1. Build an ETL pipeline for e-commerce data.
2. Design a star-schema data warehouse.
3. Demonstrate OLAP operations including roll-up, drill-down, slice, dice and pivot.
4. Segment customers using RFM and K-Means.
5. Classify repeat-purchase behavior using Random Forest.
6. Discover product relationships using Apriori-style association rule mining.
7. Generate business insights and recommendations.
8. Present results through an interactive Power BI dashboard.

### 3. Functional Modules
- Data generation/collection
- Data preprocessing and ETL
- SQLite data warehouse
- OLAP analytics
- Customer intelligence
- Product association mining
- Business insight generation
- Visualization

### 4. Custom CSV Import and Refresh
The Streamlit dashboard includes a CSV import panel for six related ecommerce source files: customers, orders, order items, payments, products and returns. Before changing the dataset, the importer validates required columns, dates, numeric fields, unique identifiers and key relationships between files. On success it rebuilds the SQLite warehouse, refreshes OLAP exports, reruns mining and regenerates business insights. If a processing step fails, the previous raw CSV files and database are restored. Custom files must follow the ecommerce data model; unrelated datasets require a different schema.

### 5. Warehouse Design
The central fact table is `fact_sales`. Dimensions are Customer, Product, Date, Location and Payment. This star schema provides efficient aggregation across business dimensions.

The generated SQLite database is:

```text
ecommerce_dw.db
```

Warehouse tables:

```text
dim_customer
dim_product
dim_date
dim_location
dim_payment
fact_sales
```

### 6. ETL
**Extract:** read CSV source files.

**Transform:** remove cancelled orders, derive age groups, calculate gross sales, discounted sales, cost and profit, identify returned orders and standardize analytical keys.

**Load:** insert dimension records first, create surrogate keys, and then load transaction-level rows into `fact_sales`.

### 7. Data Mining
**K-Means:** uses Recency, Frequency and Monetary value to create customer segments such as Premium, Loyal, Regular and At Risk.

**Random Forest:** uses order count, spend, item count, average line value and recency to demonstrate repeat-purchase classification.

**Apriori-style association mining:** converts order lines into transactions, discovers frequent itemsets, and generates rules using support, confidence and lift. The implementation uses the Python standard library, so no additional association-mining package is required.

### 8. OLAP
**Roll-up:** aggregates detailed sales into higher time levels such as month, quarter and year.

**Drill-down:** moves from year to quarter, month and day.

**Slice:** selects a single dimension value, such as sales for 2026.

**Dice:** selects a sub-cube using multiple filters, such as Electronics in the South region during Q2 2026.

**Pivot:** rotates dimensions to compare categories across years.

### 9. Dashboard
The Power BI dashboard contains:

1. **Executive Overview** — revenue, profit, orders, units, customers and sales trends.
2. **Customer Intelligence** — RFM segments, customer value and repeat-purchase predictions.
3. **Product & Basket Analysis** — top products and association rules.
4. **Geographic & Time Analysis** — region/state/city performance and time trends.

### 10. Generated Outputs
After running `python -m src.run_all`, the system creates:

- `ecommerce_dw.db`
- `outputs/customer_segments.csv`
- `outputs/repeat_purchase_predictions.csv`
- `outputs/association_rules.csv`
- `outputs/business_insights.txt`
- `outputs/monthly_sales.csv`
- `outputs/category_sales.csv`
- `outputs/region_sales.csv`
- `outputs/product_sales.csv`
- `outputs/customer_rfm.csv`

### 11. Technology Stack

| Layer | Technology |
|---|---|
| Data source | CSV |
| ETL | Python, Pandas |
| Data warehouse | SQLite |
| SQL/OLAP | SQLite SQL |
| Classification | Scikit-learn Random Forest |
| Clustering | Scikit-learn K-Means |
| Association mining | Python Apriori-style implementation |
| Visualization | Power BI |
| Development | VS Code |

### 12. Expected Outcomes
The system identifies top-performing products and categories, high-value customer segments, geographic opportunities, repeat-purchase behavior and products that are commonly purchased together. The resulting dashboard converts these analytical results into business-oriented insights.

### 13. Future Enhancements
- Real-time streaming ingestion
- Slowly Changing Dimensions (SCD Type 2)
- Cloud warehouse deployment
- Recommendation API
- Churn prediction
- Sales forecasting
- Automated email alerts
- Larger real-world datasets
