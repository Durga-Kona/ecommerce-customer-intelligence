"""Validated, rollback-safe import of user-provided ecommerce CSV datasets."""
from __future__ import annotations

import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Mapping

import pandas as pd

from .config import RAW, DB_PATH, OUTPUTS, ROOT

REQUIRED_COLUMNS = {
    "customers.csv": {"customer_id", "name", "gender", "age", "city", "state", "region"},
    "orders.csv": {"order_id", "customer_id", "order_date", "status"},
    "order_items.csv": {"order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"},
    "payments.csv": {"payment_id", "order_id", "payment_method", "amount", "payment_status"},
    "products.csv": {"product_id", "product_name", "brand", "category", "sub_category", "unit_price", "unit_cost"},
    "returns.csv": {"return_id", "order_id", "product_id", "reason", "return_date"},
}
DATE_COLUMNS = {"orders.csv": ["order_date"], "returns.csv": ["return_date"]}
NUMERIC_COLUMNS = {
    "customers.csv": ["age"],
    "order_items.csv": ["quantity", "unit_price", "discount"],
    "payments.csv": ["amount"],
    "products.csv": ["unit_price", "unit_cost"],
}


def validate_csv_frames(frames: Mapping[str, pd.DataFrame]) -> list[str]:
    errors: list[str] = []
    for filename, required in REQUIRED_COLUMNS.items():
        if filename not in frames:
            errors.append(f"Missing file: {filename}")
            continue
        df = frames[filename]
        missing = sorted(required - set(df.columns))
        if missing:
            errors.append(f"{filename}: missing required columns: {', '.join(missing)}")
        if df.empty:
            errors.append(f"{filename}: file has no data rows")
        if df.columns.duplicated().any():
            errors.append(f"{filename}: duplicate column names found")

    if errors:
        return errors

    for filename, columns in DATE_COLUMNS.items():
        for column in columns:
            parsed = pd.to_datetime(frames[filename][column], errors="coerce")
            if parsed.isna().any():
                errors.append(f"{filename}: '{column}' contains empty or invalid dates")

    for filename, columns in NUMERIC_COLUMNS.items():
        for column in columns:
            values = pd.to_numeric(frames[filename][column], errors="coerce")
            if values.isna().any():
                errors.append(f"{filename}: '{column}' contains empty or non-numeric values")

    customers = frames["customers.csv"]
    orders = frames["orders.csv"]
    items = frames["order_items.csv"]
    products = frames["products.csv"]
    payments = frames["payments.csv"]
    returns = frames["returns.csv"]

    for filename, df, col in [
        ("customers.csv", customers, "customer_id"),
        ("orders.csv", orders, "order_id"),
        ("order_items.csv", items, "order_item_id"),
        ("products.csv", products, "product_id"),
    ]:
        if df[col].isna().any() or df[col].astype(str).str.strip().eq("").any():
            errors.append(f"{filename}: '{col}' cannot be blank")
        if df[col].duplicated().any():
            errors.append(f"{filename}: '{col}' must be unique")

    if not set(orders["customer_id"].astype(str)).issubset(set(customers["customer_id"].astype(str))):
        errors.append("orders.csv: one or more customer_id values do not exist in customers.csv")
    if not set(items["order_id"].astype(str)).issubset(set(orders["order_id"].astype(str))):
        errors.append("order_items.csv: one or more order_id values do not exist in orders.csv")
    if not set(items["product_id"].astype(str)).issubset(set(products["product_id"].astype(str))):
        errors.append("order_items.csv: one or more product_id values do not exist in products.csv")

    completed_ids = set(orders.loc[orders["status"].astype(str).str.casefold().eq("completed"), "order_id"].astype(str))
    if not completed_ids:
        errors.append("orders.csv: at least one order must have status 'Completed'")
    if not set(items["order_id"].astype(str)).intersection(completed_ids):
        errors.append("order_items.csv: no items match orders marked 'Completed'")
    if payments["payment_method"].isna().all():
        errors.append("payments.csv: payment_method cannot be empty for every row")
    if not set(returns["order_id"].astype(str)).issubset(set(orders["order_id"].astype(str))):
        errors.append("returns.csv: one or more order_id values do not exist in orders.csv")
    if not set(returns["product_id"].astype(str)).issubset(set(products["product_id"].astype(str))):
        errors.append("returns.csv: one or more product_id values do not exist in products.csv")

    # Catch common data-quality issues before ETL, rather than failing later in the pipeline.
    for filename, df, key in [
        ("payments.csv", payments, "payment_id"),
        ("returns.csv", returns, "return_id"),
    ]:
        if df[key].isna().any() or df[key].astype(str).str.strip().eq("").any():
            errors.append(f"{filename}: '{key}' cannot be blank")
        if df[key].duplicated().any():
            errors.append(f"{filename}: '{key}' must be unique")

    for filename, df, column in [
        ("order_items.csv", items, "quantity"),
        ("order_items.csv", items, "unit_price"),
        ("products.csv", products, "unit_price"),
        ("products.csv", products, "unit_cost"),
        ("payments.csv", payments, "amount"),
    ]:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.notna().all() and (values < 0).any():
            errors.append(f"{filename}: '{column}' cannot contain negative values")
    discounts = pd.to_numeric(items["discount"], errors="coerce")
    if discounts.notna().all() and ((discounts < 0).any() or (discounts > 1).any()):
        errors.append("order_items.csv: 'discount' must be between 0 and 1")

    return errors


def import_and_rebuild(frames: Mapping[str, pd.DataFrame]) -> dict:
    """Replace raw CSVs and rebuild all derived data; restore previous files/database on failure."""
    errors = validate_csv_frames(frames)
    if errors:
        raise ValueError("\n".join(errors))

    RAW.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ecommerce_import_") as temp_name:
        temp = Path(temp_name)
        raw_backup = temp / "raw_backup"
        raw_backup.mkdir()
        for filename in REQUIRED_COLUMNS:
            existing = RAW / filename
            if existing.exists():
                shutil.copy2(existing, raw_backup / filename)
        db_backup = temp / "ecommerce_dw.db.bak"
        if DB_PATH.exists():
            shutil.copy2(DB_PATH, db_backup)
        output_backup = temp / "outputs_backup"
        output_backup.mkdir()
        for existing in OUTPUTS.iterdir():
            if existing.is_file():
                shutil.copy2(existing, output_backup / existing.name)

        try:
            for filename in REQUIRED_COLUMNS:
                # Normalize column headers and save clean CSV text to the canonical filename.
                frame = frames[filename].copy()
                frame.columns = [str(c).strip() for c in frame.columns]
                frame.to_csv(RAW / filename, index=False)

            from .etl import load
            from .olap import export
            from .mining import run as mine
            from .insights import run as insights

            load()
            export()
            mine()
            insights()
            with sqlite3.connect(DB_PATH) as conn:
                counts = {
                    "customers": conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0],
                    "products": conn.execute("SELECT COUNT(*) FROM dim_product").fetchone()[0],
                    "sales_rows": conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0],
                }
            return counts
        except Exception:
            # Restore the source files and warehouse so a failed import does not leave a half-updated project.
            for filename in REQUIRED_COLUMNS:
                backup = raw_backup / filename
                target = RAW / filename
                if backup.exists():
                    shutil.copy2(backup, target)
                elif target.exists():
                    target.unlink()
            if db_backup.exists():
                shutil.copy2(db_backup, DB_PATH)
            elif DB_PATH.exists():
                DB_PATH.unlink()
            for existing in OUTPUTS.iterdir():
                if existing.is_file():
                    existing.unlink()
            for backup in output_backup.iterdir():
                shutil.copy2(backup, OUTPUTS / backup.name)
            raise
