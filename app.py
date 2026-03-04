import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS & STYLE (Menghilangkan GitHub & Header)
st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=5)
def read_sheet(sheet_name):
    try:
        sn_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sn_url}'
        df = pd.read_csv(url)
        df.columns = [" ".join(str(c).split()) for c in df.columns]
        return df.dropna(axis=1, how='all')
    except:
        return pd.DataFrame()

# Fungsi Format Angka Indonesia (Titik tanpa Rp)
def fmt_titik(val):
    try:
        return f"{int(val):,}".replace(',', '.')
    except:
        return str(val)

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        list_bulan = sorted(df_foto['Bulan'].unique().tolist(), key=lambda x: (x < 11, x))
        def lbl(b): return f"{ {11:'Nov', 12:'Des', 2:'Feb'}.get(b, b) } {2025 if b>=11 else 2026}"
        bln = st.radio("Pilih Periode:", list_bulan, format_func=lbl, horizontal=True)
        f_df = df_foto[df_foto['Bulan'] == bln].sort_values(by='Tanggal')
        cols = st.columns(3)
        for i, (_, r) in enumerate(f_df.iterrows()):
            with cols[i % 3]:
                st.markdown(f"### 🗓️ Tanggal {int(r['Tanggal'])}")
                st.link_button("📂 Buka Folder", str(r['Link Folder Gdrive']).strip().rstrip(','))

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_raw = read_sheet('Estimasi Biaya')
    if not df_raw.empty:
        df_clean = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()
        
        c_s, c_t = 'Harga Satuan (Rp)', 'Total Harga (Rp)'
        # Pastikan angka bersih (Numeric)
        df_clean[c_s] = pd.to_numeric(df_clean[c_s], errors='coerce').fillna(0)
        df_clean[c_t] = pd.to_numeric(df_clean[c_t], errors='coerce').fillna(0)

        # Ringkasan
        st.markdown("### 🔍 Filter Kategori")
        kat = ["Semua"] + sorted(df_clean['Kategori'].unique().tolist())
        pilih = st.selectbox("Pilih Kategori:", kat)
        df_f = df_clean if pilih == "Semua" else df_clean[df_clean['Kategori'] == pilih]

        m1, m2 = st.columns(2)
        m1.metric("Grand Total (Rp)", fmt_titik(df_clean[c_t].sum()))
        m2.metric(f"Total {pilih} (Rp)", fmt_titik(df_f[c_t].sum()))
