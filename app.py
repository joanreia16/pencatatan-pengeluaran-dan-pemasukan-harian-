# --- app.py ---
import streamlit as st
from datetime import date
from db import init_db, simpan_data, hapus_data, load_data, update_data
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Catatan Keuangan", layout="wide")

init_db()
st.title("📒 Catatan Keuangan Harian")

# Form input
with st.form("form_input"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=date.today())
        jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = st.text_input("Kategori")
    with col2:
        biaya = st.number_input("Biaya", min_value=0.0, step=1000.0, format="%0.2f")
        catatan = st.text_input("Catatan")

    submitted = st.form_submit_button("Simpan")
    if submitted:
        simpan_data(tanggal, jenis, kategori, biaya, catatan)
        st.success("✅ Data berhasil disimpan!")

# Tampilkan data
st.subheader("📊 Data Transaksi")
data = load_data()

if data.empty:
    st.info("Belum ada data.")
else:
    st.dataframe(data, use_container_width=True)

    # Tombol download
    def convert_df_to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Laporan')
        writer.close()
        output.seek(0)
        return output

    excel_file = convert_df_to_excel(data)
    st.download_button(
        label="📥 Download Laporan Excel",
        data=excel_file,
        file_name="laporan_keuangan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Edit dan Hapus per baris
    for i, row in data.iterrows():
        with st.expander(f"📝 Edit / Hapus - {row['kategori']} | {row['biaya']}", expanded=False):
            with st.form(f"form_edit_{row['id']}"):
                tanggal_baru = st.date_input("Tanggal", value=row['tanggal'].date(), key=f"tgl_{row['id']}")
                jenis_baru = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"], index=0 if row['jenis'] == "Pemasukan" else 1, key=f"jenis_{row['id']}")
                kategori_baru = st.text_input("Kategori", value=row['kategori'], key=f"kategori_{row['id']}")
                biaya_baru = st.number_input("Biaya", value=row['biaya'], key=f"biaya_{row['id']}")
                catatan_baru = st.text_input("Catatan", value=row['catatan'], key=f"catatan_{row['id']}")

                colA, colB = st.columns(2)
                with colA:
                    update_btn = st.form_submit_button("💾 Update")
                with colB:
                    hapus_btn = st.form_submit_button("🗑️ Hapus")

                if update_btn:
                    update_data(row['id'], tanggal_baru, jenis_baru, kategori_baru, biaya_baru, catatan_baru)
                    st.success("✅ Data berhasil diperbarui!")
                    st.experimental_rerun()

                if hapus_btn:
                    hapus_data(row['id'])
                    st.warning("🗑️ Data dihapus.")
                    st.experimental_rerun()
