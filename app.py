import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=5)
def read_sheet(sheet_name):
    try:
        sn_url = sheet_name.replace(" ", "%20")
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sn_url}'
        df = pd.read_csv(url)
        # Normalisasi spasi di nama kolom (Mengatasi spasi ganda)
        df.columns = [" ".join(str(c).split()) for c in df.columns]
        return df.dropna(axis=1, how='all')
    except:
        return pd.DataFrame()

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

NAMA_BULAN = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
              7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

def get_label_periode(bln):
    nama = NAMA_BULAN.get(bln, f"Bulan {bln}")
    tahun = 2025 if bln >= 11 else 2026
    return f"{nama} {tahun}"

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

def format_idr(val):
    return f"Rp {val:,.0f}".replace(',', '.')

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        list_bulan = sorted(df_foto['Bulan'].unique().tolist(), key=lambda x: (x < 11, x))
        if list_bulan:
            bln = st.radio("Pilih Periode:", list_bulan, format_func=get_label_periode, horizontal=True)
            f_df = df_foto[df_foto['Bulan'] == bln].sort_values(by='Tanggal')
            cols = st.columns(3)
            for i, (_, r) in enumerate(f_df.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"### 🗓️ Tanggal {int(r['Tanggal'])}")
                    st.link_button("📂 Buka Folder Foto", str(r['Link Folder Gdrive']).strip().rstrip(','), use_container_width=True)

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_raw = read_sheet('Estimasi Biaya')
    
    if not df_raw.empty:
        # Filter baris: Hanya ambil yang kolom 'No' berisi angka
        df_clean = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()

        # FUNGSI PEMBERSIH ANGKA YANG LEBIH KUAT
        def force_numeric(x):
            if pd.isna(x) or x == '': return 0.0
            if isinstance(x, (int, float)): return float(x)
            # Buang semua karakter kecuali angka
            s = "".join(filter(str.isdigit, str(x)))
            return float(s) if s else 0.0

        c_s = 'Harga Satuan (Rp)'
        c_t = 'Total Harga (Rp)'
        c_spec = 'Type/ Spesifikasi'

        # Pastikan kolom menjadi tipe FLOAT agar NumberColumn bisa memberikan titik
        if c_s in df_clean.columns:
            df_clean[c_s] = df_clean[c_s].apply(force_numeric)
        if c_t in df_clean.columns:
            df_clean[c_t] = df_clean[c_t].apply(force_numeric)

        st.markdown("### 🔍 Filter & Ringkasan")
        kategori_list = ["Semua Kategori"] + sorted(df_clean['Kategori'].unique().tolist())
        pilihan = st.selectbox("Pilih Kategori Barang:", kategori_list)
        
        df_final = df_clean if pilihan == "Semua Kategori" else df_clean[df_clean['Kategori'] == pilihan]

        m1, m2 = st.columns(2)
        m1.metric("Grand Total Anggaran", format_idr(df_clean[c_t].sum()))
        m2.metric(f"Total {pilihan}", format_idr(df_final[c_t].sum()))
        st.markdown("---")
        
        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', c_spec, 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_final.columns]
        
        # KONFIGURASI TABEL DENGAN FORMAT TITIK
        st.dataframe(
            df_final[show], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                c_s: st.column_config.NumberColumn("Harga Satuan", format="Rp %d"),
                c_t: st.column_config.NumberColumn("Total Harga", format="Rp %d"),
                c_spec: st.column_config.Column("Type/ Spesifikasi", width="large"),
                "No": st.column_config.Column(width="small")
            }
        )

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting & Kerjasama")
    df_d = read_sheet('Dokumen Penting')
    if not df_d.empty:
        for _, r in df_d.iterrows():
            nama = str(r['Nama Dokumen'])
            ico = "🛠️" if "Engineering" in nama else "🏁" if "Akhir" in nama else "📄"
            with st.expander(f"{ico} {nama}"):
                st.write(f"**Kategori:** {r['Kegiatan']}")
                st.link_button("Buka Dokumen", str(r['Link Unduh']))
