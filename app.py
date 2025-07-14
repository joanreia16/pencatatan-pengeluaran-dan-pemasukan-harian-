import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib.pyplot as plt

# ---------- Konfigurasi ----------
DB_FILE = 'keuangan.db'
TABLE_NAME = 'catatan_keuangan'
BATAS_PENGELUARAN_MINGGUAN = 350000

# ---------- Fungsi Database ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
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
    conn.close()

def simpan_data(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {TABLE_NAME} (Tanggal, Jenis, Kategori, Jumlah, Catatan)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['Tanggal'], data['Jenis'], data['Kategori'], data['Jumlah'], data['Catatan']))
    conn.commit()
    conn.close()

def hapus_data(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    conn.close()
    return df

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan Keuangan')
    output.seek(0)
    return output

# ---------- Inisialisasi DB ----------
init_db()

# ---------- UI Streamlit ----------
st.title("📊 Catatan Keuangan Harian")
st.markdown("Catat pengeluaran dan pemasukan harianmu dengan mudah.")

with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    jenis = st.radio("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])

    if jenis == "Pemasukan":
        kategori = st.text_input("Keterangan Pemasukan (misal: Gaji, Jualan, Bonus)")
    else:
        kategori = st.text_input("Keterangan Pengeluaran (misal: Makanan, Transportasi, Belanja)")

    biaya = st.number_input("Biaya (Rp)", min_value=0.0, step=1000.0, format="%f")
    catatan = st.text_area("Catatan", placeholder="Opsional")
    submit = st.form_submit_button("Simpan")

    if submit:
        if kategori and biaya > 0:
            data = {
                'Tanggal': tanggal.strftime("%Y-%m-%d"),
                'Jenis': jenis,
                'Kategori': kategori,
                'Jumlah': biaya,
                'Catatan': catatan
            }
            simpan_data(data)
            st.success("✅ Data berhasil disimpan!")
        else:
            st.warning("Mohon isi keterangan dan biaya dengan benar.")

# ---------- Menampilkan Data ----------
df = load_data()
st.subheader("📅 Data Keuangan")

filter_tanggal = st.date_input("Filter tanggal", [])

if isinstance(filter_tanggal, list) and len(filter_tanggal) == 2:
    start_date, end_date = filter_tanggal
    df = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

# Pisahkan menjadi 2 tabel
df_pemasukan = df[df['Jenis'] == 'Pemasukan'].sort_values(by='Tanggal', ascending=False)
df_pengeluaran = df[df['Jenis'] == 'Pengeluaran'].sort_values(by='Tanggal', ascending=False)

st.markdown("### 🟢 Tabel Pemasukan")
st.dataframe(df_pemasukan.reset_index(drop=True), use_container_width=True)

st.markdown("### 🔴 Tabel Pengeluaran")
st.dataframe(df_pengeluaran.reset_index(drop=True), use_container_width=True)

# ---------- Hapus Data ----------
if not df.empty:
    df_sorted = df.sort_values(by='Tanggal', ascending=False)
    df_sorted['Label'] = df_sorted.apply(
        lambda row: f"{row['Tanggal'].date()} | {row['Jenis']} | {row['Kategori']} | Rp {row['Jumlah']:,.0f}", axis=1
    )

    selected_labels = st.multiselect(
        "Pilih data yang ingin dihapus:",
        options=df_sorted['Label']
    )

    if st.button("Hapus Data Terpilih") and selected_labels:
        ids_terpilih = df_sorted[df_sorted['Label'].isin(selected_labels)]['id'].tolist()
        for id_ in ids_terpilih:
            hapus_data(id_)
        st.success(f"✅ {len(ids_terpilih)} data berhasil dihapus. Silakan refresh halaman.")
else:
    st.info("Belum ada data untuk dihapus.")


# ---------- Export Excel ----------
excel_file = export_excel(df)
st.download_button(
    label="📥 Download Excel",
    data=excel_file,
    file_name="laporan_keuangan.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------- Statistik ----------
st.subheader("📈 Ringkasan")
pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
saldo = pemasukan - pengeluaran

col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
col3.metric("Saldo", f"Rp {saldo:,.0f}", delta_color="inverse")

# ---------- Kesimpulan Gaya Hidup ----------
st.subheader("🧠 Kesimpulan Gaya Hidup")
if pemasukan > 0:
    rasio = pengeluaran / pemasukan
    if rasio >= 0.9:
        st.error("💸 Gaya hidup terlalu boros")
        st.write("Rekomendasi: Kurangi pengeluaran seperti jajan, nongkrong, belanja konsumtif.")
    elif 0.6 <= rasio < 0.9:
        st.info("⚖️ Gaya hidup standar")
    else:
        st.success("💰 Gaya hidup hemat")
else:
    st.warning("Belum ada data pemasukan untuk dianalisis.")

# ---------- Grafik Mingguan ----------
st.subheader("📅 Grafik Mingguan")
minggu_ini = datetime.today() - timedelta(days=6)
df_mingguan = df[df['Tanggal'] >= minggu_ini].copy()
df_mingguan['Tanggal'] = df_mingguan['Tanggal'].dt.date

if not df_mingguan.empty:
    grafik = df_mingguan.groupby(['Tanggal', 'Jenis'])['Jumlah'].sum().unstack().fillna(0)
    st.bar_chart(grafik)
else:
    st.info("Belum ada data minggu ini.")

# ---------- Grafik Pie ----------
st.subheader("🥧 Grafik Pie Pengeluaran per Kategori")
kategori_pie = df[df['Jenis'] == 'Pengeluaran'].groupby('Kategori')['Jumlah'].sum()
if not kategori_pie.empty:
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = plt.cm.Set3.colors
    ax.pie(kategori_pie, labels=kategori_pie.index, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.set_title('Distribusi Pengeluaran per Kategori')
    ax.axis('equal')
    st.pyplot(fig)
else:
    st.info("Belum ada data pengeluaran untuk pie chart.")

# ---------- Pengawasan Mingguan ----------
st.subheader("🔍 Pengawasan Mingguan")
pengeluaran_mingguan = df_mingguan[df_mingguan['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
st.write(f"Total pengeluaran minggu ini: **Rp {pengeluaran_mingguan:,.0f}**")

if pengeluaran_mingguan > BATAS_PENGELUARAN_MINGGUAN:
    st.error(f"⚠️ Melebihi batas mingguan Rp {BATAS_PENGELUARAN_MINGGUAN:,.0f}")
else:
    st.success("✅ Masih dalam batas aman.")

# ---------- Kategori Terbesar ----------
st.subheader("🏷️ Kategori Pengeluaran Terbesar")
kategori_terbesar = df[df['Jenis'] == 'Pengeluaran'].groupby('Kategori')['Jumlah'].sum()
if not kategori_terbesar.empty:
    terbesar = kategori_terbesar.idxmax()
    jumlah = kategori_terbesar.max()
    st.write(f"Kategori terbesar: **{terbesar}** (Rp {jumlah:,.0f})")
else:
    st.info("Belum ada data pengeluaran.")
