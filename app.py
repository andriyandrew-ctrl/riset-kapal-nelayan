import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=60) # Refresh data setiap 1 menit
def read_sheet(sheet_name):
    try:
        sheet_name_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name_url}'
        df = pd.read_csv(url)
        # Hapus kolom yang benar-benar kosong
        df = df.dropna(axis=1, how='all')
        # Hapus baris kosong
        df = df.dropna(subset=[df.columns[1], df.columns[2]], how='all')
        return df
    except Exception as e:
        st.error(f"Gagal membaca sheet {sheet_name}: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        bulan_pilihan = st.radio("Pilih Bulan:", [11, 12], format_func=lambda x: "November" if x==11 else "Desember", horizontal=True)
        filtered_foto = df_foto[df_foto['Bulan'] == bulan_pilihan]
        
        if filtered_foto.empty:
            st.info("Belum ada data untuk bulan ini.")
        else:
            for _, row in filtered_foto.iterrows():
                st.subheader(f"🗓️ Tanggal {int(row['Tanggal'])}")
                st.link_button(f"👉 Buka Folder Foto", str(row['Link Folder Gdrive']))
                st.divider()

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_biaya = read_sheet('Estimasi Biaya')
    if not df_biaya.empty:
        df_biaya.columns = df_biaya.columns.str.strip()

        # FUNGSI MEMBERSIHKAN ANGKA
        def clean_number(value):
            if pd.isna(value) or value == '': return 0
            s = str(value).replace('Rp', '').replace('.', '').replace(',', '').strip()
            try:
                return float(s)
            except:
                return 0

        col_total = 'Total Harga (Rp)'
        col_satuan = 'Harga Satuan (Rp)'
        
        if col_total in df_biaya.columns:
            df_biaya[col_total] = df_biaya[col_total].apply(clean_number)
        if col_satuan in df_biaya.columns:
            df_biaya[col_satuan] = df_biaya[col_satuan].apply(clean_number)
        
        # Headline Metrik
        total_biaya =
