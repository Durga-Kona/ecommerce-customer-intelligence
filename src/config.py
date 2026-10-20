from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
OUTPUTS = ROOT / 'outputs'
DB_PATH = ROOT / 'ecommerce_dw.db'

for p in (RAW, PROCESSED, OUTPUTS):
    p.mkdir(parents=True, exist_ok=True)
