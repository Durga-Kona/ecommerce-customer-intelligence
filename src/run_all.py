"""Run the DWDM pipeline without overwriting custom CSV data.

Use --generate-sample only when you explicitly want fresh demo data.
"""
import sys
from .config import RAW
from .generate_data import make
from .etl import load
from .olap import export
from .mining import run as mine
from .insights import run as insights
from .csv_import import REQUIRED_COLUMNS

if __name__ == '__main__':
    if '--generate-sample' in sys.argv or not all((RAW / name).exists() for name in REQUIRED_COLUMNS):
        make()
    load()
    export()
    mine()
    insights()
    print('COMPLETE: check outputs/ and open the Streamlit dashboard.')
