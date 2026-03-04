import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS & CSS ANTI-GITHUB
st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# CSS REVISI: Menghilangkan GitHub & Profil Akun secara total tanpa merusak navigasi
hide_github_v3 = """
    <style>
    /* 1. Sembunyikan Header Navigasi (GitHub, Deploy, Profil) */
    [data-testid="stHeaderNavView"], 
    .stAppDeployButton, 
    header [class^="viewerBadge"] {
        display: none !important;
    }

    /* 2. Sembunyikan Footer & Status Widget (Kanan Bawah) */
    footer {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* 3. Sembunyikan Menu Hamburger (Tiga Garis) */
    #MainMenu {visibility: hidden !important;}

    /* 4. Pastikan Tombol Sidebar (Panah) tetap terlihat & bisa diklik */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
    /* 5. Hilangkan garis dekorasi di bagian paling atas */
    [data-testid="stDecoration"] {display: none !important;}

    /* 6. Rapikan jarak atas agar tidak tertutup */
    .block-container {padding-top: 2rem !important;}
    </style>
"""
st.markdown(hide_github_v3, unsafe_allow_html=True)

SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=5)
def read_sheet(sheet_name):
    try:
        sn_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sn_url}'
        df = pd.read_csv(url)
        # Normalisasi spasi kolom
        df.columns = [" ".join(str(c).split()) for c in df.columns]
        return df.dropna(axis=1, how='all')
    except:
        return pd.DataFrame()

# Fungsi format angka (Hanya Titik)
def fmt_titik(val):
    try:
        if pd.isna(val) or val == '': return "0"
        return f"{int(float(val)):,}".replace(',', '.')
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
        df_clean[c_s] = pd.to_numeric(df_clean[c_s], errors='coerce').fillna(0)
        df_clean[c_t] = pd.to_numeric(df_clean[c_t], errors='coerce').fillna(0)

        kat = ["Semua"] + sorted(df_clean['Kategori'].unique().tolist())
        pilih = st.selectbox("Filter Kategori:", kat)
        df_f = df_clean if pilih == "Semua" else df_clean[df_clean['Kategori'] == pilih]

        m1, m2 = st.columns(2)
        m1.metric("Grand Total Anggaran", f"Rp {fmt_titik(df_clean[c_t].sum())}")
        m2.metric(f"Total {pilih}", f"Rp {fmt_titik(df_f[c_t].sum())}")
        
        df_disp = df_f.copy()
        df_disp[c_s] = df_disp[c_s].apply(fmt_titik)
        df_disp[c_t] = df_disp[c_t].apply(fmt_titik)
        
        cols_show = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Type/ Spesifikasi', 'Total Pemakaian', 'Satuan', c_s, c_t]
        st.dataframe(df_disp[[c for c in cols_show if c in df_disp.columns]], use_container_width=True, hide_index=True)

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting")
    df_d = read_sheet('Dokumen Penting')
    if not df_d.empty:
        for _, r in df_d.iterrows():
            with st.expander(f"📄 {r['Nama Dokumen']}"):
                st.write(f"Kegiatan: {r['Kegiatan']}")
                st.link_button("Buka Link", str(r['Link Unduh']))
