
# --- db.py ---
import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("keuangan.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        jenis TEXT,
        kategori TEXT,
        biaya REAL,
        catatan TEXT
    )''')
    conn.commit()
    conn.close()

def simpan_data(tanggal, jenis, kategori, biaya, catatan):
    conn = sqlite3.connect("keuangan.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO transaksi (tanggal, jenis, kategori, biaya, catatan) VALUES (?, ?, ?, ?, ?)",
                (tanggal.strftime("%Y-%m-%d"), jenis, kategori, biaya, catatan))
    conn.commit()
    conn.close()

def hapus_data(indexes):
    conn = sqlite3.connect("keuangan.db")
    cur = conn.cursor()
    for idx in indexes:
        cur.execute("DELETE FROM transaksi WHERE id = ?", (idx + 1,))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect("keuangan.db")
    df = pd.read_sql_query("SELECT * FROM transaksi", conn)
    conn.close()
    return df
