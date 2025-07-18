# --- app.py ---
import streamlit as st
from datetime import datetime, timedelta
from db import init_db, simpan_data, hapus_data, load_data
from utils import export_excel, tampilkan_pie_pengeluaran, tampilkan_ringkasan, tampilkan_gaya_hidup, tampilkan_kategori_terbesar

# Inisialisasi DB
init_db()

BATAS_PENGELUARAN_MINGGUAN = 350000

# --- Judul & Form Input ---
st.title("📊 Catatan Keuangan Harian")
st.markdown("Catat pengeluaran dan pemasukan harianmu dengan mudah.")

with st.form("form_keuangan"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])

    kategori = st.text_input("Kategori", placeholder="Contoh: Gaji, Makanan, Transportasi")
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
            st.experimental_rerun()
        else:
            st.warning("Mohon isi keterangan dan biaya dengan benar.")

# --- Load Data ---
df = load_data()
if df.empty:
    st.info("Belum ada data keuangan.")
    st.stop()

# --- Filter Data ---
st.sidebar.header("📂 Filter & Export")
filter_tanggal = st.sidebar.date_input("Filter Tanggal", [])
if isinstance(filter_tanggal, list) and len(filter_tanggal) == 2:
    start_date, end_date = filter_tanggal
    df = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

# --- Tampilkan Tabel ---
df_pemasukan = df[df['Jenis'] == 'Pemasukan'].sort_values(by='Tanggal', ascending=False)
df_pengeluaran = df[df['Jenis'] == 'Pengeluaran'].sort_values(by='Tanggal', ascending=False)

st.subheader("🟢 Tabel Pemasukan")
st.dataframe(df_pemasukan.reset_index(drop=True), use_container_width=True)

st.subheader("🔴 Tabel Pengeluaran")
st.dataframe(df_pengeluaran.reset_index(drop=True), use_container_width=True)

# --- Hapus Data ---
st.subheader("📋 Riwayat Terbaru & Hapus Data")
df_recent = df.sort_values(by='Tanggal', ascending=False).head(10)
for _, row in df_recent.iterrows():
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 2, 2, 2, 1])
    col1.write(row['Tanggal'].date())
    col2.write(row['Jenis'])
    col3.write(row['Kategori'])
    col4.write(f"Rp {row['Jumlah']:,.0f}")
    col5.write(row['Catatan'])
    if col6.button("🗑️", key=f"hapus_{row['id']}"):
        hapus_data(row['id'])
        st.success(f"Data tanggal {row['Tanggal'].date()} berhasil dihapus!")
        st.experimental_rerun()

# --- Export Excel ---
st.sidebar.download_button(
    label="📥 Download Excel",
    data=export_excel(df),
    file_name="laporan_keuangan.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Ringkasan & Analisis ---
st.subheader("📈 Ringkasan")
pemasukan, pengeluaran = tampilkan_ringkasan(df)

st.subheader("🧠 Kesimpulan Gaya Hidup")
tampilkan_gaya_hidup(pemasukan, pengeluaran)

# --- Grafik Mingguan ---
st.subheader("📅 Grafik Mingguan")
minggu_ini = datetime.today() - timedelta(days=6)
df_mingguan = df[df['Tanggal'] >= minggu_ini].copy()
df_mingguan['Tanggal'] = df_mingguan['Tanggal'].dt.date
if not df_mingguan.empty:
    grafik = df_mingguan.groupby(['Tanggal', 'Jenis'])['Jumlah'].sum().unstack().fillna(0)
    st.bar_chart(grafik)
else:
    st.info("Belum ada data minggu ini.")

# --- Pie Chart ---
st.subheader("🥧 Grafik Pie Pengeluaran per Kategori")
tampilkan_pie_pengeluaran(df_pengeluaran)

# --- Pengawasan Mingguan ---
st.subheader("🔍 Pengawasan Mingguan")
pengeluaran_mingguan = df_mingguan[df_mingguan['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
st.write(f"Total pengeluaran minggu ini: **Rp {pengeluaran_mingguan:,.0f}**")

if pengeluaran_mingguan > BATAS_PENGELUARAN_MINGGUAN:
    st.error(f"⚠️ Melebihi batas mingguan Rp {BATAS_PENGELUARAN_MINGGUAN:,.0f}")
else:
    st.success("✅ Masih dalam batas aman.")

# --- Kategori Terbesar ---
st.subheader("🏷️ Kategori Pengeluaran Terbesar")
tampilkan_kategori_terbesar(df_pengeluaran)
