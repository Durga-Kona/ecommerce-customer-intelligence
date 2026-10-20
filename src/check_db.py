import sqlite3
from .config import DB_PATH


def main():
    with sqlite3.connect(DB_PATH) as conn:
        print(f'Database: {DB_PATH}')
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for (name,) in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            print(f'{name:18} {count:>8} rows')


if __name__ == '__main__':
    main()
