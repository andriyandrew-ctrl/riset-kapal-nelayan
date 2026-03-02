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
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    try:
        df_biaya = read_sheet('Estimasi Biaya')
        
        # Bersihkan nama kolom dari spasi berlebih (Sering jadi penyebab Error)
        df_biaya.columns = df_biaya.columns.str.strip()

        # Konversi kolom harga ke angka secara paksa
        col_total = 'Total Harga (Rp)'
        if col_total in df_biaya.columns:
            df_biaya[col_total] = pd.to_numeric(df_biaya[col_total].astype(str).str.replace('.', '').str.replace(',', ''), errors='coerce').fillna(0)
        
        # Metrik Atas
        total_biaya = df_biaya[col_total].sum() if col_total in df_biaya.columns else 0
        st.metric("Total Anggaran Keseluruhan", f"Rp {total_biaya:,.0f}")
        
        # Menampilkan Tabel Utama
        # Kita definisikan kolom yang ingin ditampilkan agar rapi
        kolom_target = ['No', 'Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', 'Harga Satuan (Rp)', 'Total Harga (Rp)']
        
        # Filter kolom yang benar-benar ada di sheet
        cols_to_show = [c for c in kolom_target if c in df_biaya.columns]
        
        st.dataframe(
            df_biaya[cols_to_show], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Harga Satuan (Rp)": st.column_config.NumberColumn(format="Rp %d"),
                "Total Harga (Rp)": st.column_config.NumberColumn(format="Rp %d")
            }
        )
        
    except Exception as e:
        st.error(f"Detail Error: {e}")

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
