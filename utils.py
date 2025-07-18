# --- utils.py ---
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as st

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan Keuangan')
    output.seek(0)
    return output

def tampilkan_pie_pengeluaran(df_pengeluaran):
    kategori_pie = df_pengeluaran.groupby('Kategori')['Jumlah'].sum()
    if not kategori_pie.empty:
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = plt.cm.Set3.colors
        ax.pie(kategori_pie, labels=kategori_pie.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title('Distribusi Pengeluaran per Kategori')
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("Belum ada data pengeluaran untuk pie chart.")

def tampilkan_ringkasan(df):
    pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
    saldo = pemasukan - pengeluaran
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {pemasukan:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {pengeluaran:,.0f}")
    col3.metric("Saldo", f"Rp {saldo:,.0f}", delta_color="inverse")
    return pemasukan, pengeluaran

def tampilkan_gaya_hidup(pemasukan, pengeluaran):
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

def tampilkan_kategori_terbesar(df_pengeluaran):
    kategori_terbesar = df_pengeluaran.groupby('Kategori')['Jumlah'].sum()
    if not kategori_terbesar.empty:
        terbesar = kategori_terbesar.idxmax()
        jumlah = kategori_terbesar.max()
        st.write(f"Kategori terbesar: **{terbesar}** (Rp {jumlah:,.0f})")
    else:
        st.info("Belum ada data pengeluaran.")
