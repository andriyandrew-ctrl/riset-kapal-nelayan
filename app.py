import streamlit as st
import sqlite3
import pandas as pd

# Konfigurasi Halaman agar tampil Wah
st.set_page_config(page_title="R&D Riset Kapal", layout="wide", page_icon="⚓")

# Menu Navigasi di Sidebar
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["🏠 Dashboard", "📅 Timeline Riset", "📁 Dokumen Kemdikti (Folder 02)"])

# Fungsi Koneksi Database
def load_data(query):
    conn = sqlite3.connect('database.db')
    data = pd.read_sql(query, conn)
    conn.close()
    return data

if menu == "🏠 Dashboard":
    st.title("⚓ Dashboard Riset Kapal Nelayan")
    st.markdown("---")
    st.write("Selamat datang di sistem manajemen riset terpadu.")
    st.info("Gunakan menu di sebelah kiri untuk melihat timeline kegiatan atau dokumen.")

elif menu == "📅 Timeline Riset":
    st.title("📅 Timeline & Progres Kegiatan")
    df = load_data("SELECT * FROM riset_utama ORDER BY tanggal DESC")
    
    for _, row in df.iterrows():
        with st.expander(f"📌 {row['tanggal']} - {row['judul_kegiatan']}"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Progres", f"{row['progres_persen']}%")
            with c2:
                st.write(f"**Bulan:** {row['bulan']}")
                st.write(f"**Keterangan:** {row['keterangan']}")
                st.markdown(f"[📸 Folder Foto]({row['link_folder_foto']}) | [📄 Notulen]({row['link_notulen']})")

elif menu == "📁 Dokumen Kemdikti (Folder 02)":
    st.title("📁 Dokumen KEMDIKTIKSAINTEK")
    df_doc = load_data("SELECT * FROM dokumen_penting")
    st.dataframe(df_doc, use_container_width=True)
