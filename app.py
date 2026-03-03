import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=10)
def read_sheet(sheet_name):
    try:
        sn_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sn_url}'
        df = pd.read_csv(url)
        # Hapus kolom yang benar-benar kosong
        df = df.dropna(axis=1, how='all')
        return df
    except Exception:
        return pd.DataFrame()

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# Fungsi format rupiah
def format_idr(val):
    return f"Rp {val:,.0f}".replace(',', '.')

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        bln = st.radio("Pilih Bulan:", [11, 12], format_func=lambda x: "November" if x==11 else "Desember", horizontal=True)
        if 'Bulan' in df_foto.columns:
            f_df = df_foto[df_foto['Bulan'] == bln]
            for _, r in f_df.iterrows():
                st.subheader(f"🗓️ Tanggal {int(r['Tanggal'])}")
                st.link_button("👉 Buka Folder Foto", str(r['Link Folder Gdrive']))
                st.divider()

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_raw = read_sheet('Estimasi Biaya')
    
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        
        # Filter: Ambil baris yang No-nya angka (abaikan baris TOTAL)
        df_b = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()

        def safe_num(x):
            if pd.isna(x) or x == '': return 0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('Rp', '').replace(' ', '').replace('.', '').replace(',', '')
            return float(s) if s.isdigit() else 0

        c_t, c_s = 'Total Harga (Rp)', 'Harga Satuan (Rp)'
        if c_t in df_b.columns: df_b[c_t] = df_b[c_t].apply(safe_num)
        if c_s in df_b.columns: df_b[c_s] = df_b[c_s].apply(safe_num)

        t_anggaran = df_b[c_t].sum()
        st.metric("Total Anggaran Proyek", format_idr(t_anggaran))
        st.markdown("---")

        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_b.columns]
        
        st.dataframe(
            df_b[show],
            use_container_width=True,
            hide_index=True,
            column_config={
                c_s: st.column_config.NumberColumn("Harga Satuan (Rp)", format="Rp %d"),
                c_t: st.column_config.NumberColumn("Total Harga (Rp)", format="Rp %d"),
                "No": st.column_config.Column(width="small"),
                "Total Pemakaian": st.column_config.Column(width="small")
            }
        )

# --- MENU 3: DOKUMEN PENTING (UPDATE) ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting & Kerjasama")
    df_d = read_sheet('Dokumen Penting')
    
    if not df_d.empty:
        df_d.columns = df_d.columns.str.strip()
        
        # Menampilkan dokumen dalam bentuk kartu expander
        for _, r in df_d.iterrows():
            # Ikon berbeda untuk setiap jenis dokumen
            icon = "📄"
            if "Engineering" in str(r['Nama Dokumen']): icon = "🛠️"
            elif "Laporan Akhir" in str(r['Nama Dokumen']): icon = "🏁"
            elif "Proposal" in str(r['Nama Dokumen']): icon = "📝"
            
            with st.expander(f"{icon} {r['Nama Dokumen']}"):
                st.write(f"**Kategori Kegiatan:** {r['Kegiatan']}")
                st.info(f"Klik tombol di bawah untuk mengakses file di Google Drive.")
                st.link_button("
