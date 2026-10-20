import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.csv_import import REQUIRED_COLUMNS, validate_csv_frames, import_and_rebuild

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "ecommerce_dw.db"
OUT = ROOT / "outputs"

st.set_page_config(page_title="E-Commerce Intelligence Platform", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.kpi {padding: 14px 18px; border-radius: 14px; background: linear-gradient(135deg,#f8fafc,#eef2ff); border: 1px solid #e2e8f0;}
.kpi-label {font-size:.82rem;color:#64748b;margin-bottom:2px}.kpi-value{font-size:1.55rem;font-weight:700;color:#0f172a}
.insight {padding: 12px 16px; border-left: 4px solid #4f46e5; background:#f8fafc; border-radius:8px; margin-bottom:8px;}
.csv-import-banner {padding: 1rem 1.2rem; border-radius: 12px; border: 2px solid #4f46e5; background: linear-gradient(110deg, rgba(79,70,229,.10), rgba(14,165,233,.07)); margin: .4rem 0 1rem 0;}
.csv-import-banner h3 {margin: 0 0 .35rem 0; color: #3730a3;}
.csv-import-hint {font-size: .95rem; margin-bottom: .2rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=120)
def load_data():
    conn = sqlite3.connect(DB)
    sales = pd.read_sql_query("""
        SELECT f.*, d.full_date, d.year, d.month, d.month_name, d.quarter,
               c.customer_id, c.name AS customer_name, c.gender, c.age_group,
               c.city AS customer_city, c.state AS customer_state, c.region AS customer_region,
               p.product_id, p.product_name, p.brand, p.category, p.sub_category,
               l.city, l.state, l.region, pm.payment_method
        FROM fact_sales f
        JOIN dim_date d ON d.date_key=f.date_key
        JOIN dim_customer c ON c.customer_key=f.customer_key
        JOIN dim_product p ON p.product_key=f.product_key
        JOIN dim_location l ON l.location_key=f.location_key
        LEFT JOIN dim_payment pm ON pm.payment_key=f.payment_key
    """, conn)
    customers = pd.read_sql_query("SELECT * FROM dim_customer", conn)
    products = pd.read_sql_query("SELECT * FROM dim_product", conn)
    conn.close()
    sales["full_date"] = pd.to_datetime(sales["full_date"], errors="coerce")
    return sales, customers, products

# Keep CSV import discoverable without taking up dashboard space.
with st.popover("📥 Import / Update CSV Dataset", use_container_width=True):
    st.markdown("### Upload your ecommerce CSV files")
    st.caption("Upload all six files. The current dataset is replaced only after validation succeeds. Use the files in `data/raw/` as templates and keep the required column names and matching IDs.")
    with st.form("csv_import_form", clear_on_submit=False):
        uploaded = {}
        upload_cols = st.columns(2)
        for index, filename in enumerate(REQUIRED_COLUMNS):
            with upload_cols[index % 2]:
                uploaded_file = st.file_uploader(filename, type=["csv"], key=f"upload_{filename}")
                if uploaded_file is not None:
                    try:
                        uploaded[filename] = pd.read_csv(uploaded_file, dtype=str)
                    except Exception as exc:
                        st.error(f"Could not read {filename}: {exc}")
        import_clicked = st.form_submit_button("✅ Validate CSVs and update dashboard", type="primary", use_container_width=True)

    if import_clicked:
        missing_files = [name for name in REQUIRED_COLUMNS if name not in uploaded]
        if missing_files:
            st.error("Please upload all six files: " + ", ".join(missing_files))
        else:
            validation_errors = validate_csv_frames(uploaded)
            if validation_errors:
                st.error("The files need fixing before import:")
                for message in validation_errors:
                    st.write(f"• {message}")
            else:
                try:
                    with st.spinner("Importing CSVs, rebuilding the SQLite warehouse, and refreshing analytics..."):
                        result = import_and_rebuild(uploaded)
                        load_data.clear()
                    st.success("Dataset imported successfully. The dashboard is refreshed with your data.")
                    st.write(f"Customers: {result['customers']:,} · Products: {result['products']:,} · Sales rows: {result['sales_rows']:,}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Import failed. The previous CSV files and database were restored. Details: {exc}")

sales, customers, products = load_data()

st.title("🛒 E-Commerce Customer Intelligence & Sales Analytics")
st.caption("Data Warehousing + OLAP + Data Mining + Business Intelligence")

# Sidebar
st.sidebar.header("🎛️ Global Filters")
years = sorted(sales.year.dropna().unique().tolist())
categories = sorted(sales.category.dropna().unique().tolist())
regions = sorted(sales.region.dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Year", years, default=years)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
if not sales.empty and sales["full_date"].notna().any():
    min_date = sales["full_date"].min().date()
    max_date = sales["full_date"].max().date()
    selected_dates = st.sidebar.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
else:
    selected_dates = ()

filtered = sales[sales.year.isin(selected_years) & sales.category.isin(selected_categories) & sales.region.isin(selected_regions)].copy()
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    filtered = filtered[filtered.full_date.dt.date.between(selected_dates[0], selected_dates[1])]
if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# KPI helper
def kpis(df):
    revenue = df.sales_amount.sum()
    profit = df.profit.sum()
    orders = df.order_id.nunique()
    cust = df.customer_id.nunique()
    units = df.quantity.sum()
    margin = (profit / revenue * 100) if revenue else 0
    return revenue, profit, orders, cust, units, margin

revenue, profit, orders, cust, units, margin = kpis(filtered)
cols = st.columns(6)
for col, label, value in [
    (cols[0], "Revenue", f"₹{revenue:,.0f}"),
    (cols[1], "Profit", f"₹{profit:,.0f}"),
    (cols[2], "Orders", f"{orders:,}"),
    (cols[3], "Customers", f"{cust:,}"),
    (cols[4], "Units Sold", f"{units:,}"),
    (cols[5], "Profit Margin", f"{margin:.1f}%"),
]:
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

st.divider()

# Navigation tabs
home, sales_tab, customer_tab, product_tab, olap_tab, quality_tab = st.tabs([
    "🏠 Executive Overview", "📈 Sales Analytics", "👥 Customer Intelligence", "🛍️ Product & Basket", "🧊 OLAP Explorer", "🧪 Data Quality"
])

with home:
    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.subheader("Revenue & Profit Trend")
        monthly = filtered.groupby(["year","month","month_name"], as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum"))
        monthly["period"] = pd.to_datetime(monthly.year.astype(str)+"-"+monthly.month.astype(str)+"-01")
        monthly = monthly.sort_values("period")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly.period, y=monthly.revenue, mode="lines+markers", name="Revenue"))
        fig.add_trace(go.Scatter(x=monthly.period, y=monthly.profit, mode="lines+markers", name="Profit"))
        fig.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Sales by Category")
        cat = filtered.groupby("category", as_index=False).agg(revenue=("sales_amount","sum")).sort_values("revenue")
        fig = px.bar(cat, x="revenue", y="category", orientation="h", text_auto=".2s")
        fig.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Sales by Region")
        reg = filtered.groupby("region", as_index=False).agg(revenue=("sales_amount","sum")).sort_values("revenue", ascending=False)
        fig = px.bar(reg, x="region", y="revenue", text_auto=".2s")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.subheader("Payment Method Mix")
        pay = filtered.groupby("payment_method", as_index=False).agg(revenue=("sales_amount","sum"))
        fig = px.pie(pay, names="payment_method", values="revenue", hole=.45)
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("💡 Insights from the current filters")
    if not filtered.empty:
        best_category = filtered.groupby("category")["sales_amount"].sum().idxmax()
        best_region = filtered.groupby("region")["sales_amount"].sum().idxmax()
        best_product = filtered.groupby("product_name")["sales_amount"].sum().idxmax()
        st.markdown(f'<div class="insight">Highest-revenue category in this selection: <b>{best_category}</b>.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight">Highest-revenue region in this selection: <b>{best_region}</b>.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight">Top product by revenue in this selection: <b>{best_product}</b>.</div>', unsafe_allow_html=True)
        if len(monthly) >= 2:
            previous, latest = monthly.iloc[-2], monthly.iloc[-1]
            if previous.revenue:
                change = (latest.revenue - previous.revenue) / previous.revenue * 100
                st.markdown(f'<div class="insight">Revenue changed by <b>{change:+.1f}%</b> from {previous.period:%b %Y} to {latest.period:%b %Y}. This compares the last two months present in the filtered data.</div>', unsafe_allow_html=True)

with sales_tab:
    st.subheader("Detailed Sales Analytics")
    c1, c2 = st.columns(2)
    with c1:
        quarter = filtered.groupby(["year","quarter"], as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum"))
        quarter["period"] = quarter.year.astype(str)+" Q"+quarter.quarter.astype(str)
        fig = px.bar(quarter, x="period", y="revenue", text_auto=".2s", title="Quarterly Revenue")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        age = filtered.groupby("age_group", as_index=False).agg(revenue=("sales_amount","sum"), orders=("order_id","nunique"))
        fig = px.bar(age, x="age_group", y="revenue", text_auto=".2s", title="Revenue by Age Group")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top Cities")
    city = filtered.groupby(["city","state"], as_index=False).agg(revenue=("sales_amount","sum"), orders=("order_id","nunique"), profit=("profit","sum")).sort_values("revenue", ascending=False).head(15)
    st.dataframe(city, use_container_width=True, hide_index=True)

with customer_tab:
    st.subheader("Customer Intelligence")
    seg_file = OUT / "customer_segments.csv"
    rfm_file = OUT / "customer_rfm.csv"
    if seg_file.exists():
        seg = pd.read_csv(seg_file)
        c1, c2 = st.columns([1,1.4])
        with c1:
            if "segment" in seg:
                counts = seg.segment.value_counts().reset_index()
                counts.columns = ["segment","customers"]
                fig = px.pie(counts, names="segment", values="customers", hole=.45, title="Customer Segments")
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if {"segment","monetary"}.issubset(seg.columns):
                value = seg.groupby("segment", as_index=False).agg(customers=("customer_id","count"), revenue=("monetary","sum"), avg_monetary=("monetary","mean")).sort_values("revenue", ascending=False)
                st.dataframe(value, use_container_width=True, hide_index=True)
    else:
        st.info("Run the mining pipeline first.")
    if rfm_file.exists():
        rfm = pd.read_csv(rfm_file)
        st.subheader("RFM Customer Table")
        st.dataframe(rfm.sort_values("monetary", ascending=False).head(30), use_container_width=True, hide_index=True)

with product_tab:
    st.subheader("Product Performance & Market Basket")
    c1, c2 = st.columns([1.3,1])
    with c1:
        prod = filtered.groupby(["product_name","category"], as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum"), units=("quantity","sum")).sort_values("revenue", ascending=False).head(15)
        fig = px.bar(prod, x="revenue", y="product_name", orientation="h", color="category", text_auto=".2s", title="Top Products")
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        assoc_file = OUT / "association_rules.csv"
        if assoc_file.exists():
            assoc = pd.read_csv(assoc_file)
            st.markdown("**Strongest product associations**")
            if not assoc.empty:
                cols_show = [c for c in ["antecedents","consequents","support","confidence","lift"] if c in assoc.columns]
                st.dataframe(assoc[cols_show].head(15), use_container_width=True, hide_index=True)
            else:
                st.info("No association rules met the thresholds.")
        else:
            st.info("Run the mining pipeline first.")

with olap_tab:
    st.subheader("🧊 OLAP Explorer")
    st.caption("Use these controls to demonstrate Slice, Dice, Roll-up and Drill-down operations.")
    op = st.selectbox("OLAP operation", ["Roll-up: Revenue by Year", "Drill-down: Year → Quarter → Month", "Slice: Selected Year", "Dice: Category + Region", "Pivot: Category × Year"])
    if op.startswith("Roll-up"):
        d = filtered.groupby("year", as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum"))
        st.dataframe(d, use_container_width=True, hide_index=True)
        st.bar_chart(d.set_index("year")["revenue"])
    elif op.startswith("Drill-down"):
        d = filtered.groupby(["year","quarter","month","month_name"], as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum")).sort_values(["year","month"])
        st.dataframe(d, use_container_width=True, hide_index=True)
    elif op.startswith("Slice"):
        yr = st.selectbox("Choose year", years)
        d = sales[sales.year == yr].groupby("category", as_index=False).agg(revenue=("sales_amount","sum"), profit=("profit","sum")).sort_values("revenue", ascending=False)
        st.dataframe(d, use_container_width=True, hide_index=True)
    elif op.startswith("Dice"):
        d = filtered.groupby(["category","region"], as_index=False).agg(revenue=("sales_amount","sum"), orders=("order_id","nunique")).sort_values("revenue", ascending=False)
        st.dataframe(d, use_container_width=True, hide_index=True)
    else:
        p = filtered.pivot_table(index="category", columns="year", values="sales_amount", aggfunc="sum", fill_value=0)
        st.dataframe(p, use_container_width=True)
        st.bar_chart(p)

st.divider()
with st.expander("🔎 View detailed sales records"):
    cols = ["order_id","full_date","customer_id","customer_name","product_name","category","city","state","quantity","sales_amount","profit","payment_method"]
    st.dataframe(filtered[cols].sort_values("full_date", ascending=False), use_container_width=True, height=430, hide_index=True)

st.caption("E-Commerce Customer Intelligence & Sales Analytics Platform • DWDM Academic Project")


with quality_tab:
    st.subheader("Data quality and dataset profile")
    st.caption("These checks describe the warehouse rows currently available to the dashboard. CSV import validation also checks source files and relationships before rebuilding the warehouse.")
    quality = pd.DataFrame([
        {"Check": "Sales fact rows", "Result": f"{len(sales):,}", "Status": "Info"},
        {"Check": "Distinct customers in sales", "Result": f"{sales.customer_id.nunique():,}", "Status": "Info"},
        {"Check": "Distinct products in sales", "Result": f"{sales.product_id.nunique():,}", "Status": "Info"},
        {"Check": "Missing order dates", "Result": f"{sales.full_date.isna().sum():,}", "Status": "Pass" if not sales.full_date.isna().any() else "Review"},
        {"Check": "Missing sales amount", "Result": f"{sales.sales_amount.isna().sum():,}", "Status": "Pass" if not sales.sales_amount.isna().any() else "Review"},
        {"Check": "Missing profit", "Result": f"{sales.profit.isna().sum():,}", "Status": "Pass" if not sales.profit.isna().any() else "Review"},
        {"Check": "Non-positive quantities", "Result": f"{(sales.quantity <= 0).sum():,}", "Status": "Pass" if (sales.quantity > 0).all() else "Review"},
    ])
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.subheader("Warehouse table counts")
    count_rows = []
    try:
        with sqlite3.connect(DB) as conn:
            for table in ["fact_sales", "dim_customer", "dim_product", "dim_date", "dim_location", "dim_payment"]:
                count_rows.append({"Table": table, "Rows": conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]})
    except sqlite3.Error as exc:
        st.error(f"Could not inspect warehouse tables: {exc}")
    if count_rows:
        st.dataframe(pd.DataFrame(count_rows), use_container_width=True, hide_index=True)
    st.subheader("Export filtered rows")
    export_csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered sales as CSV", data=export_csv, file_name="filtered_sales.csv", mime="text/csv")
