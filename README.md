# E-Commerce Customer Intelligence & Sales Analytics

A portfolio-ready Data Warehousing and Business Intelligence project built with Python, Pandas, SQLite, Streamlit and Plotly. It demonstrates a repeatable ETL pipeline, a star-schema warehouse, OLAP operations, customer segmentation, market-basket analysis, and an interactive dashboard.

> **Dataset note:** The included CSVs are synthetic demonstration data. Do not describe them as real company data. Monetary values use the sample project's ₹ display convention; change the display currency if your dataset uses another currency.

## Dashboard features

- Executive KPIs: revenue, profit, distinct orders, customers, units and profit margin.
- Global filters for year, category, region and order-date range.
- Revenue/profit trends, category and regional performance, payment mix and product rankings.
- Customer segmentation/RFM outputs and association-rule results from the mining pipeline.
- OLAP demonstrations: roll-up, drill-down, slice, dice and pivot.
- Data-quality profile, warehouse row counts and filtered-sales CSV download.
- CSV import validation across six related files; import attempts rebuild the warehouse and analytical outputs, with backup/restore on failure.

## Architecture

```text
Six related source CSVs
        | validation + Pandas ETL
        v
SQLite star schema (fact_sales + dimensions)
        |                         |
        v                         v
OLAP / SQL analytics       Data mining outputs
        \                         /
         v                       v
          Streamlit + Plotly dashboard
```

## Project structure

```text
data/raw/             Six source CSV templates
src/dashboard.py      Streamlit application
src/csv_import.py     CSV validation and rollback-safe import
src/etl.py            Transform/load into SQLite
src/olap.py           Export OLAP aggregates
src/mining.py         RFM, segmentation, prediction and association rules
src/insights.py       Business insight generation
src/run_all.py        Run the full analytics pipeline
sql/schema.sql        Warehouse schema
sql/olap_queries.sql  OLAP examples
sql/interview_analysis.sql  Window functions, CTEs and BI queries
outputs/              Generated analytics CSVs and insight text
tests/                Smoke tests
```

## Run locally (Windows PowerShell)

Python 3.11 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run src/dashboard.py
```

If the SQLite database or generated analytics outputs are absent or stale, run the pipeline once:

```powershell
python -m src.run_all
```

Run automated smoke tests from the project root:

```powershell
python -m unittest discover -s tests -v
```

## CSV import format

Use the six example files in `data/raw/` as templates: `customers.csv`, `orders.csv`, `order_items.csv`, `payments.csv`, `products.csv`, and `returns.csv`. The importer expects the required column names and linked IDs. It rejects missing files/columns, invalid dates and numeric values, duplicate key IDs, broken customer/order/product references, negative amounts/quantities, and discounts outside 0–1. Keep a backup of important data before importing. The dashboard replaces the active dataset; it does not append new records.

## Deploy to Streamlit Community Cloud

1. Push the project to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and branch.
3. Set **Main file path** to `src/dashboard.py`.
4. Deploy and test the app using its public URL.

The repository includes the sample SQLite database and generated outputs so the first cloud render can display the demo. Streamlit's local filesystem is not a durable database service: CSV uploads and rebuilt SQLite/output files on a hosted instance may be lost after a restart or redeploy. Re-upload the dataset when needed, or add persistent external storage for a long-lived hosted demo. Do not upload private or sensitive data to a public repository. A public repository exposes all committed files to everyone.

## Data model and metric definitions

- **Fact grain:** one row per order item/sales line in `fact_sales`, not one row per order.
- **Revenue:** sum of `fact_sales.sales_amount`.
- **Profit:** sum of `fact_sales.profit` as computed by the ETL rules.
- **Orders:** distinct `order_id` count, not fact-row count.
- **Profit margin:** total profit divided by total revenue, multiplied by 100.
- **Customer count:** distinct customer IDs represented in the filtered sales rows.

Check `sql/schema.sql`, `sql/olap_queries.sql`, and `sql/interview_analysis.sql` before interviews so you can explain the joins, table grain and assumptions. Predictive outputs are exploratory demo analyses and should not be described as production-grade predictions without a separate evaluation.

## Portfolio presentation checklist

- Add screenshots of the dashboard to the README after deployment.
- Explain the business question, data model, ETL stages, validation rules and at least three findings supported by the sample data.
- Mention limitations honestly: synthetic data, local SQLite persistence, and the need to evaluate predictive models before using them for decisions.
