# --- db.py ---
import sqlite3
from datetime import datetime

DB_NAME = "data_keuangan.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS keuangan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT,
            kategori TEXT,
            biaya REAL,
            catatan TEXT
        )
    ''')
    conn.commit()
    conn.close()

def simpan_data(tanggal, jenis, kategori, biaya, catatan):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO keuangan (tanggal, jenis, kategori, biaya, catatan)
        VALUES (?, ?, ?, ?, ?)
    """, (tanggal, jenis, kategori, biaya, catatan))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM keuangan ORDER BY tanggal DESC")
    data = c.fetchall()
    conn.close()
    return data

def hapus_data(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM keuangan WHERE id=?", (id,))
    conn.commit()
    conn.close()

def update_data(id, tanggal, jenis, kategori, biaya, catatan):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE keuangan SET tanggal=?, jenis=?, kategori=?, biaya=?, catatan=?
        WHERE id=?
    """, (tanggal, jenis, kategori, biaya, catatan, id))
    conn.commit()
    conn.close()
