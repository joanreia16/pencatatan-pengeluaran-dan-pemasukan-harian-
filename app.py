
# --- app.py ---
import streamlit as st
from datetime import datetime, timedelta
from db import init_db, simpan_data, hapus_data, load_data
from utils import export_excel, tampilkan_pie_pengeluaran, tampilkan_ringkasan, tampilkan_gaya_hidup, tampilkan_kategori_terbesar

# Inisialisasi DB
init_db()

BATAS_PENGELUARAN_MINGGUAN = 350000

# --- Judul & Form Input ---
st.title("📒 Catatan Keuangan Harian")
st.markdown("Catat pengeluaran dan pemasukan harianmu dengan mudah.")

with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    kategori = st.text_input("Kategori", placeholder="Contoh: Gaji, Makanan, Transportasi")
    biaya = st.number_input("Biaya (Rp)", min_value=0.0, format="%f")
    catatan = st.text_area("Catatan", placeholder="Opsional")
    submit = st.form_submit_button("Simpan")

if submit:
    simpan_data(tanggal, jenis, kategori, biaya, catatan)
    st.success("Data berhasil disimpan!")

# --- Tabel Data ---
st.subheader("📊 Riwayat Transaksi")
data = load_data()

if data.empty:
    st.info("Belum ada data.")
else:
    st.dataframe(data)

    # Hapus data
    hapus = st.multiselect("Pilih index yang ingin dihapus", data.index)
    if st.button("Hapus Data"):
        hapus_data(hapus)
        st.success("Data berhasil dihapus.")

    # Ekspor Excel
    st.download_button("📥 Download Excel", export_excel(data), file_name="catatan_keuangan.xlsx")

    # Ringkasan
    tampilkan_ringkasan(data)
    tampilkan_pie_pengeluaran(data)
    tampilkan_gaya_hidup(data, BATAS_PENGELUARAN_MINGGUAN)
    tampilkan_kategori_terbesar(data)
