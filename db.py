# --- db.py ---
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "data_keuangan.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE,
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
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transaksi (tanggal, jenis, kategori, biaya, catatan) VALUES (?, ?, ?, ?, ?)",
                   (tanggal, jenis, kategori, biaya, catatan))
    conn.commit()
    conn.close()

def hapus_data(id_transaksi):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaksi WHERE id=?", (id_transaksi,))
    conn.commit()
    conn.close()

def update_data(id_transaksi, tanggal, jenis, kategori, biaya, catatan):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transaksi
        SET tanggal=?, jenis=?, kategori=?, biaya=?, catatan=?
        WHERE id=?
    """, (tanggal, jenis, kategori, biaya, catatan, id_transaksi))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaksi ORDER BY tanggal DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return pd.DataFrame()  # Kembalikan DataFrame kosong jika tidak ada data

    df = pd.DataFrame(rows, columns=["id", "tanggal", "jenis", "kategori", "biaya", "catatan"])
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df
