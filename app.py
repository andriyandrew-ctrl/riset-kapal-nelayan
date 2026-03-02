# --- MENU 2: ESTIMASI BIAYA (VERSI PRO) ---
elif menu == "💰 Estimasi Biaya":
    st.title("💰 Dashboard Estimasi Biaya Proyek")
    st.markdown("Monitor anggaran fabrikasi dan pengadaan komponen secara real-time.")
    
    try:
        # Load data
        df_biaya = read_sheet('Estimasi Biaya')
        
        # --- TAHAP PEMBERSIHAN (Cleaning) ---
        # 1. Hapus kolom yang mengandung kata 'Unnamed'
        df_biaya = df_biaya.loc[:, ~df_biaya.columns.str.contains('^Unnamed')]
        # 2. Hapus baris yang Nama Barang-nya kosong
        df_biaya = df_biaya.dropna(subset=['Nama Barang'])
        # 3. Pastikan kolom harga adalah angka
        df_biaya['Total Harga (Rp)'] = pd.to_numeric(df_biaya['Total Harga (Rp)'], errors='coerce').fillna(0)

        # --- BAGIAN ATAS: RINGKASAN (METRICS) ---
        total_proyek = df_biaya['Total Harga (Rp)'].sum()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Anggaran Keseluruhan", f"Rp {total_proyek:,.0f}")
        with col_m2:
            items_count = len(df_biaya)
            st.metric("Jumlah Item Barang", f"{items_count} Item")
        with col_m3:
            # Mengambil kategori dengan biaya terbesar
            top_kat = df_biaya.groupby('Kategori')['Total Harga (Rp)'].sum().idxmax()
            st.metric("Pengeluaran Terbesar", top_kat)

        st.markdown("---")

        # --- BAGIAN TENGAH: ANALISIS PER KATEGORI ---
        st.subheader("📊 Ringkasan Biaya per Kategori")
        df_summary = df_biaya.groupby('Kategori')['Total Harga (Rp)'].sum().reset_index()
        df_summary = df_summary.sort_values('Total Harga (Rp)', ascending=False)
        
        # Menampilkan ringkasan biaya dalam kolom yang rapi
        rekap_cols = st.columns(len(df_summary))
        for i, row in df_summary.iterrows():
            rekap_cols[i].write(f"**{row['Kategori']}**")
            rekap_cols[i].write(f"Rp {row['Total Harga (Rp)']:,.0f}")

        st.markdown("---")

        # --- BAGIAN BAWAH: TABEL DETAIL ---
        st.subheader("📋 Detail Daftar Pengadaan")
        
        # Filter Pencarian Profesional
        search = st.text_input("🔍 Cari Nama Barang atau Merk...", "")
        
        # Filter Kategori Multi-select
        pilihan_kat = st.multiselect("Filter Kategori:", 
                                     options=df_biaya['Kategori'].unique(), 
                                     default=df_biaya['Kategori'].unique())
        
        # Terapkan Filter
        mask = (df_biaya['Kategori'].isin(pilihan_kat)) & \
               (df_biaya['Nama Barang'].str.contains(search, case=False, na=False))
        df_final = df_biaya[mask]

        # Menampilkan Tabel dengan styling (Hanya kolom yang diperlukan)
        kolom_pilihan = ['Kategori', 'Nama Barang', 'Merk/Ukuran', 'Total Pemakaian', 'Satuan', 'Total Harga (Rp)']
        
        st.dataframe(
            df_final[kolom_pilihan],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total Harga (Rp)": st.column_config.NumberColumn(format="Rp %d"),
                "Total Pemakaian": st.column_config.NumberColumn(format="%d")
            }
        )
        
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")
