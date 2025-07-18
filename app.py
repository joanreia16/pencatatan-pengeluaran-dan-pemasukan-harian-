
# --- app.py ---
import streamlit as st
from datetime import datetime, timedelta
from db import init_db, simpan_data, hapus_data, load_data
from utils import export_excel, tampilkan_pie_pengeluaran, tampilkan_ringkasan, tampilkan_gaya_hidup, tampilkan_kategori_terbesar

# Inisialisasi DB
init_db()

BATAS_PENGELUARAN_MINGGUAN = 350000
# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from db import init_db, simpan_data, hapus_data, update_data, load_data

# Inisialisasi DB
init_db()

st.title("📋 Catatan Keuangan Harian")
st.markdown("Catat pengeluaran dan pemasukan harianmu dengan mudah.")

# Ambil data dari database
data = load_data()

# Cek apakah sedang mengedit data
edit_data = None
if 'edit_id' in st.session_state:
    edit_id = st.session_state.edit_id
    edit_data = data[data['id'] == edit_id].iloc[0] if not data.empty else None

# Form Input
with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", value=edit_data['tanggal'] if edit_data is not None else datetime.today())
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"], index=0 if edit_data is None else ["Pemasukan", "Pengeluaran"].index(edit_data['jenis']))
    kategori = st.text_input("Kategori", value=edit_data['kategori'] if edit_data is not None else "")
    biaya = st.number_input("Biaya (Rp)", min_value=0.0, value=float(edit_data['biaya']) if edit_data is not None else 0.0, format="%f")
    catatan = st.text_area("Catatan", value=edit_data['catatan'] if edit_data is not None else "", placeholder="Opsional")
    submit = st.form_submit_button("Simpan")

if submit:
    if edit_data is not None:
        update_data(edit_data['id'], tanggal, jenis, kategori, biaya, catatan)
        st.success("Data berhasil diperbarui!")
        del st.session_state.edit_id
    else:
        simpan_data(tanggal, jenis, kategori, biaya, catatan)
        st.success("Data berhasil disimpan!")
    st.experimental_rerun()

# Menampilkan Data
st.subheader("📄 Riwayat Transaksi")
data = load_data()
if not data.empty:
    for i, row in data.iterrows():
        st.markdown(f"**{row['tanggal']} | {row['jenis']} | {row['kategori']} | Rp {row['biaya']}**")
        st.markdown(f"Catatan: {row['catatan']}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_id = row['id']
                st.experimental_rerun()
        with col2:
            if st.button("🗑️ Hapus", key=f"hapus_{row['id']}"):
                hapus_data(row['id'])
                st.success("Data berhasil dihapus!")
                st.experimental_rerun()
else:
    st.info("Belum ada data transaksi.")

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
