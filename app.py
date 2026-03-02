import streamlit as st
import pandas as pd

# ==========================================
# 1. SETUP IDENTITAS (PASTIKAN ID SHEET BENAR)
# ==========================================
# Ganti ID di bawah dengan ID dari URL Google Sheets Anda
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

def read_sheet(sheet_name):
    # Mengubah spasi jadi format URL agar tidak error
    sheet_name_url = sheet_name.replace(" ", "%20")
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name_url}'
    return pd.read_csv(url)

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# SIDEBAR NAVIGASI
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    try:
        df_foto = read_sheet('Foto Kegiatan')
        
        # Pilihan Bulan
        bulan_pilihan = st.radio("Pilih Bulan:", [11, 12], 
                                 format_func=lambda x: "November" if x==11 else "Desember", 
                                 horizontal=True)
        
        # Filter Data berdasarkan kolom 'Bulan'
        filtered_foto = df_foto[df_foto['Bulan'] == bulan_pilihan]
        
        if filtered_foto.empty:
            st.warning(f"Data untuk bulan ini belum tersedia di Google Sheets.")
        else:
            for _, row in filtered_foto.iterrows():
                # Headline Tanggal
                st.subheader(f"🗓️ Tanggal {int(row['Tanggal'])}")
                st.info(f"Deskripsi: {row['Keterangan'] if pd.notna(row['Keterangan']) else '-'}")
                st.link_button(f"👉 Buka Folder Foto", str(row['Link Folder Gdrive']))
                st.divider()
    except Exception as e:
        st.error(f"Error: Pastikan nama Tab 'Foto Kegiatan' sudah benar. Detail: {e}")

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    try:
        df_biaya = read_sheet('Estimasi Biaya')
        
        # Menghitung Total dari kolom 'Total Harga (Rp)'
        # Pastikan kolom ini di Google Sheets berisi angka, bukan teks
        total_anggaran = pd.to_numeric(df_biaya['Total Harga (Rp)'], errors='coerce').sum()
        
        st.metric("Total Estimasi Anggaran Proyek", f"Rp {total_anggaran:,.0f}")
        
        # Filter Kategori
        list_kategori = df_biaya['Kategori'].unique()
        pilihan_kat = st.multiselect("Filter Kategori:", list_kategori, default=list_kategori)
        
        df_display = df_biaya[df_biaya['Kategori'].isin(pilihan_kat)]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: Pastikan nama Tab 'Estimasi Biaya' sudah benar. Detail: {e}")

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting")
    try:
        df_doc = read_sheet('Dokumen Penting')
        
        for _, row in df_doc.iterrows():
            with st.expander(f"📄 {row['Nama Dokumen']}"):
                st.write(f"**Kategori:** {row['Kegiatan']}")
                st.link_button("Buka Link Dokumen", str(row['Link Unduh']))
    except Exception as e:
        st.error(f"Error: Pastikan nama Tab 'Dokumen Penting' sudah benar. Detail: {e}")
