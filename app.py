import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Riset Kapal Nelayan ITS", layout="wide", page_icon="🚢")

# Custom CSS untuk tampilan lebih profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def load_sql_data(query):
    conn = sqlite3.connect('database.db')
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/id/0/00/Logo_ITS.png", width=100)
st.sidebar.title("R&D Navigasi")
menu = st.sidebar.selectbox("Pilih Menu:", 
    ["🏠 Dashboard", "📸 Koleksi Foto Kegiatan", "📊 Timeline Progress Project", "💰 Estimasi Part & Consumable", "📁 Dokumen Penting"])

if menu == "🏠 Dashboard":
    st.title("⚓ Dashboard Riset Kapal Nelayan 8 GT")
    st.write("Sistem Monitoring Terpadu: Foto Kegiatan, Dokumen Kerjasama, dan Estimasi Kebutuhan Part.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Status Proyek", "Fabrikasi")
    col2.metric("Lokasi", "ITS Surabaya")
    col3.metric("Target", "Mock-Up 8 GT")
    
    st.image("https://images.unsplash.com/photo-1544216717-3bbf52512659?q=80&w=2070&auto=format&fit=crop", caption="Proses Fabrikasi Kapal Baja")

elif menu == "📸 Koleksi Foto Kegiatan":
    st.title("📸 Koleksi Foto Kegiatan")
    bulan_opt = st.radio("Pilih Periode:", ["November", "Desember"], horizontal=True)
    
    df = load_sql_data(f"SELECT * FROM riset_utama WHERE bulan = '{bulan_opt}' ORDER BY tanggal DESC")
    
    if df.empty:
        st.warning(f"Belum ada data kegiatan untuk bulan {bulan_opt}")
    else:
        for _, row in df.iterrows():
            with st.container():
                st.subheader(f"📅 {row['tanggal']} - {row['judul_kegiatan']}")
                st.write(f"ℹ️ {row['keterangan']}")
                st.link_button(f"📁 Buka Folder Foto {row['tanggal']}", row['link_folder_foto'])
                st.divider()

elif menu == "📊 Timeline Progress Project":
    st.title("📊 Timeline & Progress Project")
    st.info("STEEL FISHING VESSEL 8 GT MOCK UP FABRICATION TIMELINE")
    
    # Ringkasan dari Excel Timeline yang anda kirim
    st.write("### Ringkasan Jadwal Fabrikasi")
    data_timeline = {
        "Main Activity": ["Marking & Cutting", "Assembling Bottom", "Assembling Side Shell", "Deck Construction", "Painting"],
        "Bulan": ["November", "November-Desember", "Desember", "Desember-Januari", "Januari"],
        "Status": ["Selesai", "In-Progress", "In-Progress", "Planned", "Planned"]
    }
    st.table(pd.DataFrame(data_timeline))
    st.success("Capaian Kumulatif: Sesuai dengan Target Rencana")

elif menu == "💰 Estimasi Part & Consumable":
    st.title("💰 Estimasi Kebutuhan & Biaya")
    st.write("Berdasarkan Estimasi Kebutuhan Consumable & Part Riset Kapal")
    
    # Ringkasan Biaya dari Excel Anda
    t1, t2, t3 = st.tabs(["⚙️ Parts & Elektrik", "👨‍🏭 Fabrikasi & Las", "🎨 Pengecatan"])
    
    with t1:
        st.subheader("Kategori Parts & Elektrik")
        st.write("**Total Estimasi: Rp 72.428.000**")
        st.write("- Mesin Honda BF20 (20 HP)\n- Sistem Kemudi\n- Sistem Navigasi Radio (Icom M220)\n- GPS & Pompa")
        
    with t2:
        st.subheader("Kategori Fabrikasi & Pengelasan")
        st.write("**Total Estimasi: Rp 21.837.250**")
        st.write("- Batu Gerinda Poles & Potong (WD)\n- Kawat Las FCAW & CHE 58-1\n- Wire Brush & Amplas Susun")
        
    with t3:
        st.subheader("Kategori Pengecatan")
        st.write("**Total Estimasi: Rp 14.921.500**")
        st.write("- Cat Primer Epoxy White\n- Top Coat Acrylic Grey (Jotun Pioneer)\n- Thinner & Alat Cat (Kuas/Roll)")

elif menu == "📁 Dokumen Penting":
    st.title("📁 Dokumen Kerjasama & Internal")
    df_doc = load_sql_data("SELECT * FROM dokumen_penting")
    
    for _, row in df_doc.iterrows():
        with st.container():
            col_a, col_b = st.columns([0.8, 0.2])
            col_a.write(f"**{row['nama_dokumen']}**")
            col_a.caption(f"Kategori: {row['kategori']}")
            col_b.link_button("Buka Folder", row['link_unduh'])
            st.divider()
