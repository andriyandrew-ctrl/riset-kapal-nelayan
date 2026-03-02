import streamlit as st
import pandas as pd

# ==========================================
# 1. SETUP IDENTITAS (PASTIKAN ID SHEET BENAR)
# ==========================================
# Ganti kode di bawah dengan ID Google Sheets Anda
SHEET_ID = 1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8

def read_sheet(sheet_name):
    # Nama sheet harus persis sama dengan yang ada di Google Sheets
    sheet_name_fixed = sheet_name.replace(" ", "%20")
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name_fixed}'
    return pd.read_csv(url)

# Konfigurasi Tampilan
st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# Custom CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- MENU 1: KOLEKSI FOTO ---
if menu == "Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    st.write("Daftar dokumentasi kegiatan per tanggal.")
    
    try:
        df_foto = read_sheet('Foto Kegiatan')
        
        # Pilihan Bulan
        bulan_pilihan = st.radio("Pilih Bulan:", [11, 12], 
                                 format_func=lambda x: "November" if x==11 else "Desember", 
                                 horizontal=True)
        
        # Filter Data
        filtered_foto = df_foto[df_foto['Bulan'] == bulan_pilihan]
        
        if filtered_foto.empty:
            st.warning(f"Data untuk bulan ini belum tersedia.")
        else:
            for _, row in filtered_foto.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    # Headline Tanggal
                    col1.subheader(f"🗓️ Tgl {int(row['Tanggal'])}")
                    with col2:
                        st.info(f"Keterangan: {row['Keterangan'] if pd.notna(row['Keterangan']) else 'Tidak ada keterangan'}")
                        st.link_button(f"👉 Lihat Foto Kegiatan", row['Link Folder Gdrive'])
                    st.divider()
    except Exception as e:
        st.error(f"Gagal memuat data Foto: {e}")

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    
    try:
        df_biaya = read_sheet('Estimasi Biaya')
        
        # Bersihkan data (hapus baris kosong jika ada)
        df_biaya = df_biaya.dropna(subset=['Nama Barang'])

        # Dashboard Metrik
        total_anggaran = df_biaya['Total Harga (Rp)'].sum()
        st.metric("Total Estimasi Anggaran Proyek", f"Rp {total_anggaran:,.0f}")
        
        # Filter Kategori
        list_kategori = df_biaya['Kategori'].unique()
        pilihan_kat = st.multiselect("Filter Kategori:", list_kategori, default=list_kategori)
        
        df_display = df_biaya[df_biaya['Kategori'].isin(pilihan_kat)]
        
        # Tampilkan Tabel
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Gagal memuat data Biaya: {e}")

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "Dokumen Penting":
    st.title("📁 Dokumen Kerjasama & Internal")
    
    try:
        df_doc = read_sheet('Dokumen Penting')
        
        for _, row in df_doc.iterrows():
            with st.expander(f"📄 {row['Nama Dokumen']}"):
                st.write(f"**Instansi/Kegiatan:** {row['Kegiatan']}")
                st.link_button("Buka Folder Dokumen", row['Link Unduh'])
                
    except Exception as e:
        st.error(f"Gagal memuat data Dokumen: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("R&D Riset Kapal Nelayan 8GT ITS © 2024")
