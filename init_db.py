import sqlite3
import requests
import os
from dotenv import load_dotenv

# Load .env so init_db works whether run standalone or via the app
load_dotenv()

FRANKFURTER_CURRENCIES_URL = "https://api.frankfurter.dev/v2/currencies"


def init_db(db_path=None):
    """
    Initialize the SQLite database and cache currency symbols from Frankfurter.
    No API key required. Idempotent: safe to call repeatedly — only fetches
    when the symbols table is empty.
    """
    db_path = os.getenv("DB_PATH", "currency_cache.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            code TEXT PRIMARY KEY,
            name TEXT
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM symbols')
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"Database already contains {count} currency symbols.")
        conn.close()
        return

    # Table is empty — fetch from Frankfurter (no key required).
    # /v2/currencies returns a JSON array of objects:
    #   [{"iso_code": "USD", "name": "United States Dollar", ...}, ...]
    try:
        response = requests.get(FRANKFURTER_CURRENCIES_URL, timeout=10)
        response.raise_for_status()
        symbols = response.json()

        for entry in symbols:
            code = entry.get("iso_code")
            name = entry.get("name")
            if not code or not name:
                continue
            cursor.execute(
                'INSERT OR IGNORE INTO symbols (code, name) VALUES (?, ?)',
                (code, name),
            )
        conn.commit()
        print(f"Successfully cached {len(symbols)} currency symbols from Frankfurter.")
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching symbols: {e}")
    except Exception as e:
        print(f"Unexpected error fetching symbols: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
