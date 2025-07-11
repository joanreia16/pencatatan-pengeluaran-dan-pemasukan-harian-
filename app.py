
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# ---------- Konfigurasi ----------
CSV_FILE = 'data_keuangan.csv'

# ---------- Fungsi ----------
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=['Tanggal', 'Jenis', 'Kategori', 'Jumlah', 'Catatan'])
        df.to_csv(CSV_FILE, index=False)
        return df

def simpan_data(data_baru):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# ---------- UI Streamlit ----------
st.title("📊 Catatan Keuangan Harian")
st.markdown("Catat pengeluaran dan pemasukan harianmu dengan mudah.")

with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    jenis = st.radio("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    kategori = st.text_input("Kategori / Barang")
    jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%f")
    catatan = st.text_area("Catatan", placeholder="Opsional")
    submit = st.form_submit_button("Simpan")

    if submit:
        if kategori and jumlah > 0:
            data = {
                'Tanggal': tanggal.strftime("%Y-%m-%d"),
                'Jenis': jenis,
                'Kategori': kategori,
                'Jumlah': jumlah,
                'Catatan': catatan
            }
            simpan_data(data)
            st.success("✅ Data berhasil disimpan!")
        else:
            st.warning("Mohon isi kategori dan jumlah dengan benar.")

# ---------- Menampilkan Data ----------
df = load_data()
df['Tanggal'] = pd.to_datetime(df['Tanggal'])
st.subheader("📅 Data Keuangan")

filter_tanggal = st.date_input("Filter tanggal", [])

if isinstance(filter_tanggal, list) and len(filter_tanggal) == 2:
    start_date, end_date = filter_tanggal
    df = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

st.dataframe(df.sort_values(by='Tanggal', ascending=False), use_container_width=True)

# ---------- Statistik dan Grafik ----------
st.subheader("📈 Ringkasan")

pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
saldo = pemasukan - pengeluaran

col1, col2, col3 = st.columns(3)
col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
col3.metric("Saldo", f"Rp {saldo:,.0f}", delta_color="inverse")

# Grafik mingguan
st.subheader("📅 Grafik Mingguan")
minggu_ini = datetime.today() - timedelta(days=6)
df_mingguan = df[df['Tanggal'] >= minggu_ini]

if not df_mingguan.empty:
    grafik = df_mingguan.groupby(['Tanggal', 'Jenis'])['Jumlah'].sum().unstack().fillna(0)
    st.bar_chart(grafik)
else:
    st.info("Belum ada data minggu ini.")
