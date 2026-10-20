import sqlite3
import unittest
from pathlib import Path
import pandas as pd
from src.csv_import import REQUIRED_COLUMNS, validate_csv_frames
ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_sample_csvs_pass_validation(self):
        frames = {name: pd.read_csv(ROOT / 'data' / 'raw' / name, dtype=str) for name in REQUIRED_COLUMNS}
        self.assertEqual(validate_csv_frames(frames), [])

    def test_missing_required_file_is_reported(self):
        frames = {name: pd.read_csv(ROOT / 'data' / 'raw' / name, dtype=str) for name in REQUIRED_COLUMNS if name != 'returns.csv'}
        self.assertTrue(any('Missing file: returns.csv' in e for e in validate_csv_frames(frames)))

    def test_duplicate_customer_ids_are_reported(self):
        frames = {name: pd.read_csv(ROOT / 'data' / 'raw' / name, dtype=str) for name in REQUIRED_COLUMNS}
        frames['customers.csv'] = pd.concat([frames['customers.csv'], frames['customers.csv'].iloc[[0]]], ignore_index=True)
        self.assertTrue(any("customer_id' must be unique" in e for e in validate_csv_frames(frames)))

    def test_warehouse_tables_exist_and_have_data(self):
        db = ROOT / 'ecommerce_dw.db'
        self.assertTrue(db.exists())
        with sqlite3.connect(db) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({'fact_sales','dim_customer','dim_product','dim_date','dim_location','dim_payment'}.issubset(tables))
            self.assertGreater(conn.execute('SELECT COUNT(*) FROM fact_sales').fetchone()[0], 0)

    def test_interview_sql_syntax(self):
        script = (ROOT / 'sql' / 'interview_analysis.sql').read_text(encoding='utf-8')
        with sqlite3.connect(ROOT / 'ecommerce_dw.db') as conn:
            conn.executescript(script)

if __name__ == '__main__':
    unittest.main()
