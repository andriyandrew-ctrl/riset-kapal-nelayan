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
        bln = st.radio("Pilih Bulan:", [11, 12], format_func=lambda x: "November" if x==11 else "Desember", horizontal=True)
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
        df_b = df_raw[pd.to_numeric(df_raw['No'], errors='coerce').notnull()].copy()

        def cln(x):
            if pd.isna(x) or x == '': return 0
            if isinstance(x, (int, float)): return float(x)
            s = str(x).replace('Rp', '').replace(' ', '').replace('.', '').replace(',', '')
            return float(s) if s.isdigit() else 0

        c_t, c_s = 'Total Harga (Rp)', 'Harga Satuan (Rp)'
        if c_t in df_b.columns: df_b[c_t] = df_b[c_t].apply(cln)
        if c_s in df_b.columns: df_b[c_s] = df_b[c_s].apply(cln)

        st.metric("Total Anggaran Proyek", format_idr(df_b[c_t].sum()))
        st.markdown("---")
        
        target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', c_s, c_t]
        show = [c for c in target if c in df_b.columns]
        st.dataframe(df_b[show], use_container_width=True, hide_index=True,
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
            # Tentukan ikon berdasarkan nama dokumen
            ico = "🛠️" if "Engineering" in nama else "🏁" if "Akhir" in nama else "📄"
            
            with st.expander(f"{ico} {nama}"):
                st.write(f"**Kategori:** {r['Kegiatan']}")
                # Baris di bawah ini sering error jika terputus, saya buat sangat singkat:
                st.link_button("Buka Dokumen", str(r['Link Unduh']))
    else:
        st.info("Dokumen tidak ditemukan.")
