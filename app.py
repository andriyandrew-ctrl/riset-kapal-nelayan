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
        # Normalisasi spasi di nama kolom
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

# FUNGSI FORMAT RUPIAH DENGAN TITIK (HASILNYA TEKS)
def format_idr(val):
    try:
        if pd.isna(val) or val == '': return "Rp 0"
        # Ambil angka saja
        s = "".join(filter(str.isdigit, str(val)))
        if not s: return "Rp 0"
        return f"Rp {int(s):,.0f}".replace(',', '.')
    except:
        return "Rp 0"

# FUNGSI PEMBERSIH ANGKA MURNI (UNTUK PERHITUNGAN)
def to_float(val):
    try:
        s = "".join(filter(str.isdigit, str(val)))
        return float(s) if s else 0.0
    except:
        return 0.0

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
        # Filter baris: Hanya yang ada nomornya
        df_clean = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()

        c_s = 'Harga Satuan (Rp)'
        c_t = 'Total Harga (Rp)'
        c_spec = 'Type/ Spesifikasi'

        # 1. HITUNG TOTAL DULU (MENGGUNAKAN ANGKA MURNI)
        total_proyek = df_clean[c_t].apply(to_float).sum()

        st.markdown("### 🔍 Filter & Ringkasan")
        kategori_list = ["Semua Kategori"] + sorted(df_clean['Kategori'].unique().tolist())
        pilihan = st.selectbox("Pilih Kategori Barang:", kategori_list)
        
        df_final = df_clean if pilihan == "Semua Kategori" else df_clean[df_clean['Kategori'] == pilihan]
        total_sub = df_final[c_t].apply(to_float).sum()

        # Metrik Atas
        m1, m2 = st.columns(2)
        m1.metric("Grand Total Anggaran", format_idr(total_proyek))
        m2.metric(f"Total {pilihan}", format_idr(total_sub))
        st.markdown("---")
        
        # 2. UBAH KOLOM HARGA MENJADI TEKS BERFORMAT (TITIK RIBUAN) SEBELUM TAMPIL
        df_display = df_final.copy()
        df_display[c_s] = df_display[c_s].apply(format_idr)
        df_display[c_t] = df_display[c_t].apply(format_idr)

        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', c_spec, 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_display.columns]
        
        # DISPLAY TABEL (Menggunakan TextColumn agar titik tidak hilang)
        st.dataframe(
            df_display[show], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                c_s: st.column_config.TextColumn("Harga Satuan"),
                c_t: st.column_config.TextColumn("Total Harga"),
                c_spec: st.column_config.Column("Type/ Spesifikasi", width="large")
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
