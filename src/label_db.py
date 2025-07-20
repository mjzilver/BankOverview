import sqlite3
import pandas as pd
import os

DB_PATH = "data/labels.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                Tegenpartij TEXT PRIMARY KEY,
                Label TEXT,
                Zakelijk BOOLEAN
            )
        """)

def save_label(tegenpartij, label, zakelijk):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO labels (Tegenpartij, Label, Zakelijk)
            VALUES (?, ?, ?)
            ON CONFLICT(Tegenpartij) DO UPDATE SET
                Label=excluded.Label,
                Zakelijk=excluded.Zakelijk
        """, (tegenpartij, label, zakelijk))

def get_labels():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM labels", conn)
