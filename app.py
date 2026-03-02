import streamlit as st
import pandas as pd
import re

# 1. SETUP IDENTITAS
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=60)
def read_sheet(sheet_name):
    try:
        sn_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sn_url}'
        df = pd.read_csv(url)
        df = df.dropna(axis=1, how='all').dropna(how='all')
        return df
    except Exception:
        return pd.DataFrame()

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- FUNGSI FORMAT RUPIAH MANUAL (UNTUK KEAMANAN TITIK RIBUAN) ---
def format_idr(val):
    return f"Rp {val:,.0f}".replace(',', '.')

# --- MENU 2: ESTIMASI BIAYA ---
if menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_b = read_sheet('Estimasi Biaya')
    
    if not df_b.empty:
        df_b.columns = df_b.columns.str.strip()
        
        # Fungsi pembersihan angka super ketat (Hanya ambil angka)
        def strict_clean(x):
            if pd.isna(x) or x == '': return 0
            # Ambil hanya digit angka, buang Rp, titik, koma, dsb
            s = re.sub(r'\D', '', str(x))
            return float(s) if s else 0

        c_t, c_s = 'Total Harga (Rp)', 'Harga Satuan (Rp)'
        
        # Proses data asli
        if c_t in df_b.columns: df_b[c_t] = df_b[c_t].apply(strict_clean)
        if c_s in df_b.columns: df_b[c_s] = df_b[c_s].apply(strict_clean)

        # Headline Metrik (Pasti 144.262.810)
        t_anggaran = df_b[c_t].sum()
        st.metric("Total Anggaran Proyek", format_idr(t_anggaran))
        st.markdown("---")

        # Buat kolom bayangan untuk tampilan agar RATA KANAN & ADA TITIK
        df_display = df_b.copy()
        df_display[c_s] = df_display[c_s].apply(format_idr)
        df_display[c_t] = df_display[c_t].apply(format_idr)

        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_display.columns]
        
        st.dataframe(
            df_display[show],
            use_container_width=True,
            hide_index=True,
            column_config={
                c_s: st.column_config.TextColumn("Harga Satuan (Rp)", width="medium"),
                c_t: st.column_config.TextColumn("Total Harga (Rp)", width="medium"),
            }
        )

# --- MENU 1 & 3 (DIPERSINGKAT UNTUK EFISIENSI) ---
elif menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        bln = st.radio("Pilih Bulan:", [11, 12], format_func=lambda x: "November" if x==11 else "Desember", horizontal=True)
        f_df = df_foto[df_foto['Bulan'] == bln]
        for _, r in f_df.iterrows():
            st.subheader(f"🗓️ Tanggal {int(r['Tanggal'])}")
            st.link_button("👉 Buka Folder Foto", str(r['Link Folder Gdrive']))
            st.divider()

elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Kerjasama")
    df_d = read_sheet('Dokumen Penting')
    if not df_d.empty:
        for _, r in df_d.iterrows():
            with st.expander(f"📄 {r['Nama Dokumen']}"):
                st.write(f"**Kegiatan:** {r['Kegiatan']}")
                st.link_button("Buka Link Dokumen", str(r['Link Unduh']))
