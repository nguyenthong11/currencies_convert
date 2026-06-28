import sqlite3
import requests
import os
from dotenv import load_dotenv

# Load .env so init_db works whether run standalone or via the app
load_dotenv()

def init_db(db_path='currency_cache.db'):
    """
    Initialize the SQLite database and cache currency symbols from Fixer.io API.
    Idempotent: safe to call repeatedly — only fetches when the symbols table is empty.
    """
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

    # Table is empty — try to populate from Fixer.io
    access_key = os.getenv('FIXER_IO_ACCESS_KEY')
    if not access_key:
        print("Error: FIXER_IO_ACCESS_KEY is not set. Add it to a .env file or your shell environment.")
        conn.close()
        return

    url = f'https://data.fixer.io/api/symbols?access_key={access_key}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('success'):
            symbols = data.get('symbols', {})
            for code, name in symbols.items():
                cursor.execute('INSERT OR IGNORE INTO symbols (code, name) VALUES (?, ?)', (code, name))
            conn.commit()
            print(f"Successfully cached {len(symbols)} currency symbols.")
        else:
            print(f"Failed to fetch symbols: {data.get('error', {}).get('info', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching symbols: {e}")
    except Exception as e:
        print(f"Unexpected error fetching symbols: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
