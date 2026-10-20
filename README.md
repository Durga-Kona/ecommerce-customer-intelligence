# 🛒 E-Commerce Customer Intelligence & Sales Analytics Platform

```{=html}
<p align="center">
```
`<img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" />`{=html}
`<img src="https://img.shields.io/badge/Data%20Processing-Pandas-150458?logo=pandas" />`{=html}
`<img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite" />`{=html}
`<img src="https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit" />`{=html}
`<img src="https://img.shields.io/badge/Visualization-Plotly-3F4F75?logo=plotly" />`{=html}
`<img src="https://img.shields.io/badge/Domain-DWDM-purple" />`{=html}
`<img src="https://img.shields.io/badge/Deployment-Streamlit%20Community%20Cloud-success" />`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
🚀
`<b>`{=html}`<a href="https://ecommerce-customer-intelligence114.streamlit.app/">`{=html}View
Live Dashboard`</a>`{=html}`</b>`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

## 📖 About the Project

**E-Commerce Customer Intelligence & Sales Analytics Platform** is a
web-based analytics application developed as part of a **Data
Warehousing and Data Mining (DWDM)** academic project.

The platform processes related e-commerce CSV datasets using **Python
and Pandas**, stores the transformed data in a **SQLite data
warehouse**, and presents business insights through an interactive
**Streamlit dashboard** with Plotly visualizations.

It brings sales analysis, customer segmentation, product analysis, SQL
analytics, and data-quality checks together in one place. The project is
also designed to demonstrate practical skills relevant to **Data Analyst
and Business Intelligence (BI)** roles.

> **Note:** The included datasets are sample demonstration data. The
> dashboard's results are illustrative and do not represent a real
> company's performance.

------------------------------------------------------------------------

# ✨ Key Features

## 📊 Sales Dashboard

-   Key Performance Indicators (KPIs)
-   Revenue and profit analysis
-   Order and customer summaries
-   Monthly sales trends
-   Category-wise sales analysis
-   Region-wise performance
-   Product and payment analysis
-   Interactive filters and Plotly charts

------------------------------------------------------------------------

## 🧑‍🤝‍🧑 Customer Intelligence

-   RFM (Recency, Frequency, Monetary) analysis
-   Customer segmentation
-   Repeat-purchase analysis outputs
-   Customer-focused business insights

------------------------------------------------------------------------

## 🛍️ Product Analysis

-   Product sales analysis
-   Product association / market-basket analysis
-   Identification of products that appear together in orders
-   Analytical outputs for further exploration

------------------------------------------------------------------------

## 🏗️ Data Warehouse & ETL

-   CSV data ingestion
-   Data cleaning and transformation using Pandas
-   SQLite data warehouse
-   Fact and dimension tables
-   SQL analytical queries
-   OLAP-style analysis

------------------------------------------------------------------------

## 📥 CSV Import & Data Validation

-   Compact **Import / Update CSV Dataset** interface
-   Upload six related e-commerce CSV files
-   Required-column and data validation checks
-   Checks for duplicate identifiers and selected invalid relationships
-   Rebuild the warehouse and analytics from the uploaded dataset
-   Backup and restore handling during import processing

------------------------------------------------------------------------

## 📈 Business Intelligence & OLAP

-   Sales and profit KPI analysis
-   Monthly, category, product and regional summaries
-   OLAP-style roll-up, drill-down, slice, dice and pivot analysis
-   Generated CSV outputs for additional reporting

------------------------------------------------------------------------

# 🛠 Technologies Used

  Technology                  Purpose
  --------------------------- -----------------------------------------
  Python                      Core programming and application logic
  Pandas                      Data processing and ETL
  SQLite                      Data warehouse
  SQL                         Schema design and analytical queries
  Streamlit                   Interactive web dashboard
  Plotly                      Interactive data visualizations
  CSV                         Source datasets and analytical exports
  `unittest`                  Automated tests
  Git & GitHub                Version control and source code hosting
  Streamlit Community Cloud   Application deployment

------------------------------------------------------------------------

# 🏗 System Architecture

``` text
             E-Commerce CSV Datasets
                       |
                       ▼
             Validation and Pandas ETL
                       |
                       ▼
               SQLite Data Warehouse
              (Fact and Dimension Tables)
                       |
             +---------+---------+
             |         |         |
             ▼         ▼         ▼
          SQL / OLAP  Customer  Product
           Analysis   Analysis  Analysis
             |         |         |
             +---------+---------+
                       |
                       ▼
             Streamlit + Plotly
               Analytics Dashboard
```

------------------------------------------------------------------------

# 📂 Project Structure

``` text
ecommerce_dwdm/
│
├── .streamlit/
├── data/
│   └── raw/                 # Sample e-commerce CSV files
│
├── docs/                    # Project and deployment documentation
├── outputs/                 # Generated analytics and insights
├── powerbi/                 # Power BI-related materials
├── sql/                     # Warehouse schema and SQL queries
│
├── src/
│   ├── dashboard.py         # Streamlit dashboard
│   ├── csv_import.py         # CSV validation and import
│   ├── etl.py                # ETL pipeline
│   ├── mining.py             # Customer and product analysis
│   ├── olap.py               # OLAP analysis
│   ├── insights.py           # Business insights
│   ├── run_all.py            # Run analytics pipeline
│   ├── check_db.py           # Database checks
│   └── generate_data.py      # Sample data generation utility
│
├── tests/                   # Automated tests
├── ecommerce_dw.db          # SQLite warehouse
├── requirements.txt         # Python dependencies
└── README.md
```

------------------------------------------------------------------------

# ⚙ Installation & Setup

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/Durga-Kona/ecommerce-customer-intelligence.git
```

### 2️⃣ Navigate to the Project Folder

``` bash
cd ecommerce-customer-intelligence
```

### 3️⃣ Create a Virtual Environment

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4️⃣ Install Required Packages

``` bash
python -m pip install -r requirements.txt
```

### 5️⃣ Run the Dashboard

``` bash
python -m streamlit run src/dashboard.py
```

Open the local URL displayed in the terminal, usually:

``` text
http://localhost:8501
```

### 🔄 Rebuild Analytics (When Required)

Run this from the project root when you need to rebuild the warehouse
and analytical outputs:

``` bash
python -m src.run_all
```

### 🧪 Run Tests

``` bash
python -m unittest discover -s tests -v
```

------------------------------------------------------------------------

# 📋 CSV Input Files

The import feature expects these six related e-commerce datasets:

-   `customers.csv`
-   `orders.csv`
-   `order_items.csv`
-   `payments.csv`
-   `products.csv`
-   `returns.csv`

Use the CSV files in `data/raw/` as templates for the expected column
names, data types, and formats. IDs and relationships must be consistent
across the datasets.

**Important:** Importing replaces the active dataset and rebuilds the
warehouse and analytics; it is not a general-purpose importer for
unrelated CSV files. Keep a backup before importing important data.

------------------------------------------------------------------------

# ☁️ Live Deployment

The application is deployed using **Streamlit Community Cloud**.

🔗 **Live Dashboard:**
https://ecommerce-customer-intelligence114.streamlit.app/

🔗 **GitHub Repository:**
https://github.com/Durga-Kona/ecommerce-customer-intelligence

The deployed app uses `src/dashboard.py` as its main file. Changes
pushed to the connected GitHub branch can trigger a redeployment.

> **Storage note:** Local SQLite files and uploaded data may not persist
> across every hosted-app restart or redeployment. Persistent storage
> should be configured before using the application for long-term user
> data.

------------------------------------------------------------------------

# 🧪 Testing

The repository includes automated smoke tests for selected validation,
database, and SQL behavior.

Tests can be run with:

``` bash
python -m unittest discover -s tests -v
```

Passing these tests does not guarantee every dashboard interaction or
every possible CSV import scenario is error-free.

------------------------------------------------------------------------

# 🎯 Learning Outcomes

-   Understanding ETL pipelines
-   Working with fact and dimension tables
-   Writing analytical SQL queries
-   Creating sales and profit KPIs
-   Performing RFM customer segmentation
-   Exploring product association patterns
-   Applying OLAP concepts
-   Building interactive dashboards
-   Validating CSV data and relationships
-   Deploying a Python application to the cloud

------------------------------------------------------------------------

# 🚀 Future Enhancements

-   More advanced data-quality reports
-   Expanded customer cohort and retention analysis
-   Improved evaluation of repeat-purchase models
-   Persistent cloud database and storage
-   Additional dashboard export options
-   Expanded automated tests and deployment checks

------------------------------------------------------------------------

# 🙏 Acknowledgements

Thanks to the Python, Pandas, SQLite, Streamlit, and Plotly communities
for providing the tools and documentation that support this project.

------------------------------------------------------------------------

# ⭐ If you find this project useful...

Please consider giving the repository a **⭐ Star** on GitHub.

```{=html}
<p align="center">
```
`<b>`{=html}🛒 Turning E-Commerce Data into Business Insights
📊`</b>`{=html}
```{=html}
</p>
```
