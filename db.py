# --- db.py ---
import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = 'keuangan.db'
TABLE_NAME = 'catatan_keuangan'


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Tanggal TEXT,
                Jenis TEXT,
                Kategori TEXT,
                Jumlah REAL,
                Catatan TEXT
            )
        ''')
        conn.commit()


def simpan_data(data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {TABLE_NAME} (Tanggal, Jenis, Kategori, Jumlah, Catatan)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['Tanggal'], data['Jenis'], data['Kategori'], data['Jumlah'], data['Catatan']))
        conn.commit()


def hapus_data(id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (id,))
        conn.commit()


@st.cache_data(ttl=10)
def load_data():
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    return df

