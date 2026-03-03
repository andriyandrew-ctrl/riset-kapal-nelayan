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
        return df.dropna(axis=1, how='all')
    except:
        return pd.DataFrame()

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# Mapping Nama Bulan & Logika Tahun
NAMA_BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

# Fungsi untuk menentukan tahun berdasarkan angka bulan (Logika Proyek)
def get_label_periode(bln):
    nama = NAMA_BULAN.get(bln, f"Bulan {bln}")
    # Jika bulan 11 atau 12, maka 2025. Jika bulan 1-10, maka 2026.
    tahun = 2025 if bln >= 11 else 2026
    return f"{nama} {tahun}"

# SIDEBAR
st.sidebar.title("⚓ Dashboard Riset Kapal Nelayan Baja")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

def format_idr(val):
    return f"Rp {val:,.0f}".replace(',', '.')

# --- MENU 1: KOLEKSI FOTO (DENGAN TAHUN) ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    df_foto = read_sheet('Foto Kegiatan')
    if not df_foto.empty:
        # Ambil daftar bulan unik dan urutkan (11, 12, baru kemudian 2)
        # Kita urutkan manual agar November 2025 muncul duluan daripada Februari 2026
        list_bulan = sorted(df_foto['Bulan'].unique().tolist(), key=lambda x: (x < 11, x))
        
        if list_bulan:
            bln = st.radio("Pilih Periode:", list_bulan, 
                           format_func=get_label_periode, 
                           horizontal=True)
            
            f_df = df_foto[df_foto['Bulan'] == bln].sort_values(by='Tanggal')
            
            cols = st.columns(3)
            for i, (_, r) in enumerate(f_df.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"### 🗓️ Tanggal {int(r['Tanggal'])}")
                    st.markdown(f"*{get_label_periode(bln)}*")
                    link = str(r['Link Folder Gdrive']).strip().rstrip(',')
                    st.link_button("📂 Buka Folder Foto", link, use_container_width=True)
                    st.write("---")
        else:
            st.info("Bel_um ada data periode yang tersedia.")
    else:
        st.error("Gagal memuat data foto.")

# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    df_raw = read_sheet('Estimasi Biaya')
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df_clean = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()

        def cln(x):
            if pd.isna(x) or x == '': return 0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('Rp', '').replace(' ', '').replace('.', '').replace(',', '')
            return float(s) if s.isdigit() else 0

        c_t, c_s = 'Total Harga (Rp)', 'Harga Satuan (Rp)'
        if c_t in df_clean.columns: df_clean[c_t] = df_clean[c_t].apply(cln)
        if c_s in df_clean.columns: df_clean[c_s] = df_clean[c_s].apply(cln)

        total_proyek = df_clean[c_t].sum()
        
        st.markdown("### 🔍 Filter & Ringkasan")
        kategori_list = ["Semua Kategori"] + sorted(df_clean['Kategori'].unique().tolist())
        pilihan_kategori = st.selectbox("Pilih Kategori Barang:", kategori_list)

        if pilihan_kategori == "Semua Kategori":
            df_final = df_clean
            label_sub = "Total Anggaran Keseluruhan"
        else:
            df_final = df_clean[df_clean['Kategori'] == pilihan_kategori]
            label_sub = f"Total Biaya: {pilihan_kategori}"

        m1, m2 = st.columns(2)
        m1.metric("Grand Total Anggaran", format_idr(total_proyek))
        m2.metric(label_sub, format_idr(df_final[c_t].sum()))

        st.markdown("---")
        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_final.columns]
        st.dataframe(df_final[show], use_container_width=True, hide_index=True,
                     column_config={c_s: st.column_config.NumberColumn(format="Rp %d"),
                                    c_t: st.column_config.NumberColumn(format="Rp %d")})

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting & Kerjasama")
    df_d = read_sheet('Dokumen Penting')
    if not df_d.empty:
        df_d.columns = df_d.columns.str.strip()
        for _, r in df_d.iterrows():
            nama = str(r['Nama Dokumen'])
            ico = "🛠️" if "Engineering" in nama else "🏁" if "Akhir" in nama else "📄"
            with st.expander(f"{ico} {nama}"):
                st.write(f"**Kategori:** {r['Kegiatan']}")
                st.link_button("Buka Dokumen", str(r['Link Unduh']))
