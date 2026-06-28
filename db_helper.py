import sqlite3

def get_all_symbols(db_path='currency_cache.db'):
    """
    Query the database to select all rows from the symbols table.
    Returns a dictionary mapping currency codes to their full names.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT code, name FROM symbols')
        return {code: name for code, name in cursor.fetchall()}

def is_symbol_supported(code, db_path='currency_cache.db'):
    """
    Check if a given currency code exists in the symbols table.
    Returns True if exists, False otherwise.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM symbols WHERE code = ?', (code,))
        return cursor.fetchone() is not None
