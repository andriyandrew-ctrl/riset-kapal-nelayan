import streamlit as st
import pandas as pd

# 1. SETUP IDENTITAS (PASTIKAN ID SHEET BENAR)
SHEET_ID = 'MASUKKAN_ID_GOOGLE_SHEET_ANDA_DI_SINI'

def read_sheet(sheet_name):
    # Mengonversi nama sheet ke format URL (spasi jadi %20)
    sheet_name_url = sheet_name.replace(" ", "%20")
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name_url}'
    
    # Membaca data
    df = pd.read_csv(url)
    
    # --- PROSES PEMBERSIHAN OTOMATIS (AGAR TIDAK ERROR) ---
    # 1. Hapus kolom yang tidak ada namanya (Unnamed)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # 2. Hapus baris yang benar-benar kosong
    df = df.dropna(how='all')
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
        
        # Filter (Gunakan 'Bulan' sesuai file Anda)
        filtered_foto = df_foto[df_foto['Bulan'] == bulan_pilihan]
        
        if filtered_foto.empty:
            st.info("Belum ada data untuk bulan ini.")
        else:
            for _, row in filtered_foto.iterrows():
                st.subheader(f"🗓️ Tanggal {int(row['Tanggal'])}")
                st.write(f"ℹ️ {row['Keterangan'] if pd.notna(row['Keterangan']) else '-'}")
                st.link_button(f"👉 Buka Folder Foto", str(row['Link Folder Gdrive']))
                st.divider()
    except Exception as e:
        st.error(f"Error di Tab Foto: {e}")

# --- MENU 2: ESTIMASI BIAYA (VERSI PRO & BERSIH) ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    try:
        df_biaya = read_sheet('Estimasi Biaya')
        
        # Membersihkan kolom Harga agar bisa dihitung
        # Nama kolom harus persis: Total Harga (Rp)
        kolom_harga = 'Total Harga (Rp)'
        df_biaya[kolom_harga] = pd.to_numeric(df_biaya[kolom_harga], errors='coerce').fillna(0)
        
        # Menampilkan Metrik Utama
        total_biaya = df_biaya[kolom_harga].sum()
        st.metric("Total Anggaran Keseluruhan", f"Rp {total_biaya:,.0f}")
        
        st.markdown("---")
        
        # Pilihan Kategori
        pilihan_kat = st.multiselect("Filter Kategori:", options=df_biaya['Kategori'].unique(), default=df_biaya['Kategori'].unique())
        df_display = df_biaya[df_biaya['Kategori'].isin(pilihan_kat)]
        
        # Menampilkan tabel hanya kolom yang penting saja agar 'PRO'
        kolom_inti = ['Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', 'Total Harga (Rp)']
        # Cek apakah kolom-kolom ini ada di sheet
        kolom_ada = [c for c in kolom_inti if c in df_display.columns]
        
        st.dataframe(df_display[kolom_ada], use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error di Tab Estimasi: {e}. Pastikan nama kolom 'Total Harga (Rp)' sudah benar.")

# --- MENU 3: DOKUMEN PENTING ---
elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Penting")
    try:
        df_doc = read_sheet('Dokumen Penting')
        for _, row in df_doc.iterrows():
            with st.expander(f"📄 {row['Nama Dokumen']}"):
                st.write(f"**Kategori:** {row['Kegiatan']}")
                st.link_button("Buka Link Gdrive", str(row['Link Unduh']))
    except Exception as e:
        st.error(f"Error di Tab Dokumen: {e}")
