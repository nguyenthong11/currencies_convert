import sqlite3
import os

def get_all_symbols(db_path=None):
    """
    Query the database to select all rows from the symbols table.
    Returns a dictionary mapping currency codes to their full names.
    """
    db_path = os.getenv("DB_PATH", "currency_cache.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT code, name FROM symbols')
        return {code: name for code, name in cursor.fetchall()}

def is_symbol_supported(code, db_path=None):
    """
    Check if a given currency code exists in the symbols table.
    Returns True if exists, False otherwise.
    """
    db_path = os.getenv("DB_PATH", "currency_cache.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM symbols WHERE code = ?', (code,))
        return cursor.fetchone() is not None
