import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS
SHEET_ID = '1-FhaAsVlrYUnn0tbC-ccwMMZIS7RKZ57lDho5yLBtI8'

@st.cache_data(ttl=60) # Refresh data setiap 1 menit
def read_sheet(sheet_name):
    sheet_name_url = sheet_name.replace(" ", "%20")
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name_url}'
    df = pd.read_csv(url)
    # Hapus kolom yang benar-benar kosong saja, jangan hapus kolom bernama
    df = df.dropna(axis=1, how='all')
    # Hapus baris kosong
    df = df.dropna(subset=[df.columns[1], df.columns[2]], how='all')
    return df

st.set_page_config(page_title="R&D Riset Kapal ITS", layout="wide", page_icon="🚢")

# SIDEBAR
st.sidebar.title("⚓ R&D Dashboard")
menu = st.sidebar.radio("Pilih Menu:", ["📸 Koleksi Foto", "💰 Estimasi Biaya", "📁 Dokumen Penting"])

# --- MENU 1: KOLEKSI FOTO ---
if menu == "📸 Koleksi Foto":
    st.title("📸 Koleksi Foto Kegiatan")
    try:
        df_foto = read_sheet('Foto Kegiatan')
        bulan_pilihan = st.radio("Pilih Bulan:", [11, 12], format_func=lambda x: "November" if x==11 else "Desember", horizontal=True)
        
        filtered_foto = df_foto[df_foto['Bulan'] == bulan_pilihan]
        
        if filtered_foto.empty:
            st.info("Belum ada data untuk bulan ini.")
        else:
            for _, row in filtered_foto.iterrows():
                st.subheader(f"🗓️ Tanggal {int(row['Tanggal'])}")
                st.link_button(f"👉 Buka Folder Foto", str(row['Link Folder Gdrive']))
                st.divider()
    except Exception as e:
        st.error(f"Koneksi Google Sheets bermasalah atau nama tab salah.")

# --- MENU 2: ESTIMASI BIAYA (FIXED) ---
# --- MENU 2: ESTIMASI BIAYA ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    try:
        df_biaya = read_sheet('Estimasi Biaya')
        df_biaya.columns = df_biaya.columns.str.strip()

        # FUNGSI MEMBERSIHKAN ANGKA (Agar tidak jadi 0)
        def clean_number(value):
            if pd.isna(value) or value == '': return 0
            # Hapus Rp, titik, dan spasi
            s = str(value).replace('Rp', '').replace('.', '').replace(',', '').strip()
            try:
                return float(s)
            except:
                return 0

        # Terapkan pembersihan ke kolom harga
        col_total = 'Total Harga (Rp)'
        col_satuan = 'Harga Satuan (Rp)'
        
        if col_total in df_biaya.columns:
            df_biaya[col_total] = df_biaya[col_total].apply(clean_number)
        if col_satuan in df_biaya.columns:
            df_biaya[col_satuan] = df_biaya[col_satuan].apply(clean_number)
        
        # Hitung Total Keseluruhan untuk Metrik
        total_biaya = df_biaya[col_total].sum()
        
        # Tampilan Metrik dengan format ribuan titik
        st.metric("Total Anggaran Keseluruhan", f"Rp {total_biaya:,.0f}".replace(',', '.'))
        st.markdown("---")

        # TAMPILKAN TABEL DENGAN FORMAT TITIK RIBUAN
        kolom_target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', 'Harga Satuan (Rp)', 'Total Harga (Rp)']
        cols_to_show = [c for c in kolom_target if c in df_biaya.columns]
        
        st.dataframe(
            df_biaya[cols_to_show], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Harga Satuan (Rp)": st.column_config.NumberColumn(
                    "Harga Satuan (Rp)",
                    format="Rp %d", # Ini akan memberikan pemisah ribuan otomatis
                ),
                "Total Harga (Rp)": st.column_config.NumberColumn(
                    "Total Harga (Rp)",
                    format="Rp %d", # Ini akan memberikan pemisah ribuan otomatis
                )
            }
        )
        
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting")
    try:
        df_doc = read_sheet('Dokumen Penting')
        df_doc.columns = df_doc.columns.str.strip()
        for _, row in df_doc.iterrows():
            with st.expander(f"📄 {row['Nama Dokumen']}"):
                st.write(f"**Kategori:** {row['Kegiatan']}")
                st.link_button("Buka Link Gdrive", str(row['Link Unduh']))
    except Exception as e:
        st.error(f"Gagal memuat dokumen.")
