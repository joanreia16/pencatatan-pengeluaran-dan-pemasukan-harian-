
# --- utils.py ---
import pandas as pd
import streamlit as st
import io
import matplotlib.pyplot as plt

def export_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Transaksi')
    output.seek(0)
    return output

def tampilkan_ringkasan(df):
    st.subheader("📌 Ringkasan")
    pemasukan = df[df['jenis'] == 'Pemasukan']['biaya'].sum()
    pengeluaran = df[df['jenis'] == 'Pengeluaran']['biaya'].sum()
    saldo = pemasukan - pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
    col3.metric("Saldo", f"Rp {saldo:,.0f}")

def tampilkan_pie_pengeluaran(df):
    st.subheader("📊 Distribusi Pengeluaran")
    df_pengeluaran = df[df['jenis'] == 'Pengeluaran']
    if df_pengeluaran.empty:
        st.info("Belum ada data pengeluaran.")
        return

    kategori_group = df_pengeluaran.groupby("kategori")["biaya"].sum()
    fig, ax = plt.subplots()
    kategori_group.plot.pie(autopct="%.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

def tampilkan_gaya_hidup(df, batas):
    st.subheader("🔥 Analisis Gaya Hidup")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    minggu_terakhir = df[df["tanggal"] >= (pd.Timestamp.today() - pd.Timedelta(days=7))]
    total_pengeluaran = minggu_terakhir[minggu_terakhir["jenis"] == "Pengeluaran"]["biaya"].sum()

    if total_pengeluaran > batas:
        st.warning(f"⚠️ Pengeluaran minggu ini Rp {total_pengeluaran:,.0f}, melebihi batas Rp {batas:,}")
    else:
        st.success(f"✅ Pengeluaran minggu ini Rp {total_pengeluaran:,.0f}, masih dalam batas Rp {batas:,}")

def tampilkan_kategori_terbesar(df):
    st.subheader("🏷️ Kategori Terbesar")
    df_pengeluaran = df[df["jenis"] == "Pengeluaran"]
    if df_pengeluaran.empty:
        st.info("Belum ada pengeluaran.")
        return

    kategori_terbesar = df_pengeluaran.groupby("kategori")["biaya"].sum().sort_values(ascending=False)
    st.bar_chart(kategori_terbesar)
