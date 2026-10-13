svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 880" width="100%" height="100%" style="background:#f8fafc; font-family:'Segoe UI', Inter, -apple-system, sans-serif;">
  <defs>
    <!-- Shadows & Gradients -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feOffset dx="0" dy="4" result="offset"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.08"/></feComponentTransfer>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="factGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#1e40af"/>
    </linearGradient>
    <linearGradient id="dimGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f766e"/>
      <stop offset="100%" stop-color="#115e59"/>
    </linearGradient>
    <linearGradient id="outriggerGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7c3aed"/>
      <stop offset="100%" stop-color="#6d28d9"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#475569"/>
    </marker>
  </defs>

  <!-- Title & Header -->
  <text x="650" y="42" text-anchor="middle" font-size="24" font-weight="800" fill="#0f172a">DESAIN STAR SCHEMA — NUSANTARA RETAIL GROUP (NRG)</text>
  <text x="650" y="68" text-anchor="middle" font-size="13" font-weight="500" fill="#64748b">Single Fact Table (Grain: 1 Baris per Item SKU per Transaksi per Kanal Penjualan) | Kelompok 4</text>

  <!-- Connector Lines (From Fact Table Center 650, 480) -->
  <!-- To dim_tanggal (x: 100, y: 120) -->
  <path d="M 480 380 C 350 350, 320 280, 310 240" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  <!-- To dim_produk (x: 500, y: 110) -->
  <path d="M 650 330 C 650 280, 650 250, 650 240" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  <!-- To dim_pemasok (outrigger from dim_produk) -->
  <path d="M 780 170 C 840 170, 890 170, 930 170" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- To dim_pelanggan (x: 960, y: 350) -->
  <path d="M 820 440 C 880 440, 910 440, 950 440" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  <!-- To dim_toko_kanal (x: 100, y: 550) -->
  <path d="M 480 560 C 390 560, 350 580, 310 610" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  <!-- To dim_kampanye (x: 500, y: 680) -->
  <path d="M 650 670 C 650 700, 650 710, 650 730" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
  <!-- To dim_metode_bayar (x: 960, y: 640) -->
  <path d="M 820 590 C 880 620, 910 640, 950 660" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>

  <!-- ==================== 1. DIM_TANGGAL (Top Left) ==================== -->
  <g transform="translate(60, 100)" filter="url(#shadow)">
    <rect width="250" height="230" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 240 0 Q 250 0 250 10 L 250 36 L 0 36 Z" fill="url(#dimGrad)"/>
    <text x="125" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_tanggal</text>
    <text x="15" y="58" font-size="11.5" font-weight="700" fill="#0f766e">PK | tanggal_key (INT)</text>
    <text x="15" y="78" font-size="11" fill="#334155">• tanggal (DATE)</text>
    <text x="15" y="96" font-size="11" fill="#334155">• hari (TINYINT), nama_hari</text>
    <text x="15" y="114" font-size="11" fill="#334155">• minggu_ke, bulan, nama_bulan</text>
    <text x="15" y="132" font-size="11" fill="#334155">• kuartal (1..4)</text>
    <text x="15" y="150" font-size="11" fill="#334155">• tahun (SMALLINT)</text>
    <text x="15" y="168" font-size="11" fill="#334155">• tahun_kuartal (e.g. 2023-Q1)</text>
    <text x="15" y="186" font-size="11" fill="#334155">• is_weekend (Y/N)</text>
    <rect x="15" y="200" width="220" height="18" rx="4" fill="#f0fdf4"/>
    <text x="125" y="213" text-anchor="middle" font-size="10" font-weight="600" fill="#166534">Lookup via: DATE(waktu_wib)</text>
  </g>

  <!-- ==================== 2. DIM_PRODUK (Top Center) ==================== -->
  <g transform="translate(480, 90)" filter="url(#shadow)">
    <rect width="310" height="250" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 300 0 Q 310 0 310 10 L 310 36 L 0 36 Z" fill="url(#dimGrad)"/>
    <text x="155" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_produk (SCD Type 2)</text>
    <text x="15" y="58" font-size="11.5" font-weight="700" fill="#0f766e">PK | produk_key (INT AUTO)</text>
    <text x="15" y="78" font-size="11" fill="#334155">• material_no (VARCHAR)</text>
    <text x="15" y="96" font-size="11" fill="#334155">• nama_produk, brand</text>
    <text x="15" y="114" font-size="11" fill="#334155">• kategori, sub_kategori</text>
    <text x="15" y="132" font-size="11" font-weight="600" fill="#7c3aed">FK | pemasok_key (INT)</text>
    <text x="15" y="150" font-size="11" fill="#334155">• harga_pokok / HPP (DECIMAL)</text>
    <text x="15" y="168" font-size="11" fill="#334155">• tgl_efektif_awal, tgl_efektif_akhir</text>
    <text x="15" y="186" font-size="11" fill="#334155">• is_current ('Y'/'N'), is_inferred ('Y'/'N')</text>
    <rect x="15" y="202" width="280" height="34" rx="4" fill="#ecfdf5"/>
    <text x="155" y="216" text-anchor="middle" font-size="9.5" font-weight="600" fill="#047857">Revisi HPP Dilacak Berdasarkan Riwayat ERP</text>
    <text x="155" y="229" text-anchor="middle" font-size="9.5" font-weight="500" fill="#047857">SKU Baru Non-ERP Diakomodasi (Inferred Member)</text>
  </g>

  <!-- ==================== OUTRIGGER: DIM_PEMASOK (Top Right) ==================== -->
  <g transform="translate(930, 95)" filter="url(#shadow)">
    <rect width="250" height="150" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 240 0 Q 250 0 250 10 L 250 36 L 0 36 Z" fill="url(#outriggerGrad)"/>
    <text x="125" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_pemasok (Outrigger)</text>
    <text x="15" y="58" font-size="11.5" font-weight="700" fill="#7c3aed">PK | pemasok_key (INT)</text>
    <text x="15" y="78" font-size="11" fill="#334155">• supplier_id (Natural Key)</text>
    <text x="15" y="96" font-size="11" fill="#334155">• nama_supplier (VARCHAR)</text>
    <text x="15" y="114" font-size="11" fill="#334155">• kota, kontak</text>
    <rect x="15" y="124" width="220" height="16" rx="4" fill="#faf5ff"/>
    <text x="125" y="136" text-anchor="middle" font-size="9" font-weight="600" fill="#6b21a8">Relasi Snowflake: dim_produk -> dim_pemasok</text>
  </g>

  <!-- ==================== 3. FACT_PENJUALAN (CENTER) ==================== -->
  <g transform="translate(480, 360)" filter="url(#shadow)">
    <rect width="340" height="340" rx="12" fill="#ffffff" stroke="#1d4ed8" stroke-width="2.5"/>
    <path d="M 0 12 Q 0 0 12 0 L 328 0 Q 340 0 340 12 L 340 40 L 0 40 Z" fill="url(#factGrad)"/>
    <text x="170" y="26" text-anchor="middle" font-size="15" font-weight="800" fill="#ffffff">fact_penjualan</text>
    
    <!-- Degenerate & Keys -->
    <text x="15" y="60" font-size="11" font-weight="700" fill="#1e40af">PK | fact_key (BIGINT AUTO)</text>
    <text x="15" y="77" font-size="10.5" fill="#475569">Degenerate: sumber_sistem, no_transaksi, no_baris</text>
    <line x1="15" y1="84" x2="325" y2="84" stroke="#e2e8f0" stroke-width="1"/>
    
    <!-- Foreign Keys -->
    <text x="15" y="100" font-size="11" font-weight="600" fill="#0369a1">FK | tanggal_key &#8594; dim_tanggal</text>
    <text x="15" y="117" font-size="11" font-weight="600" fill="#0369a1">FK | produk_key &#8594; dim_produk (SCD2)</text>
    <text x="15" y="134" font-size="11" font-weight="600" fill="#0369a1">FK | pelanggan_key &#8594; dim_pelanggan</text>
    <text x="15" y="151" font-size="11" font-weight="600" fill="#0369a1">FK | toko_kanal_key &#8594; dim_toko_kanal</text>
    <text x="15" y="168" font-size="11" font-weight="600" fill="#0369a1">FK | kampanye_key &#8594; dim_kampanye</text>
    <text x="15" y="185" font-size="11" font-weight="600" fill="#0369a1">FK | metode_bayar_key &#8594; dim_metode_bayar</text>
    <line x1="15" y1="193" x2="325" y2="193" stroke="#e2e8f0" stroke-width="1"/>
    
    <!-- Measures -->
    <text x="15" y="210" font-size="11" font-weight="700" fill="#0f172a">METRIK / MEASURES (Excl. PPN 11%):</text>
    <text x="15" y="226" font-size="10.5" fill="#334155">• qty (INT)</text>
    <text x="15" y="242" font-size="10.5" fill="#334155">• harga_satuan_excl, penjualan_kotor_excl</text>
    <text x="15" y="258" font-size="10.5" fill="#334155">• diskon_excl_ppn, penjualan_bersih_excl</text>
    <text x="15" y="274" font-size="10.5" fill="#334155">• harga_pokok_satuan, harga_pokok_total</text>
    <text x="15" y="290" font-size="10.5" fill="#b91c1c">• fee_komisi, fee_layanan (Alokasi MPL)</text>
    <text x="15" y="306" font-size="11" font-weight="700" fill="#15803d">&#9733; margin_kotor (Bersih - HPP - Fees)</text>
    <text x="15" y="322" font-size="10.5" fill="#334155">• qty_retur, nilai_retur_excl_ppn</text>
  </g>

  <!-- ==================== 4. DIM_PELANGGAN (Middle Right) ==================== -->
  <g transform="translate(950, 320)" filter="url(#shadow)">
    <rect width="290" height="260" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 280 0 Q 290 0 290 10 L 290 36 L 0 36 Z" fill="url(#dimGrad)"/>
    <text x="145" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_pelanggan (Omnichannel)</text>
    <text x="15" y="58" font-size="11.5" font-weight="700" fill="#0f766e">PK | pelanggan_key (INT AUTO)</text>
    <text x="15" y="76" font-size="11" font-weight="700" fill="#b45309">• tipe_pelanggan (OMNICHANNEL / WEB / POS / MPL)</text>
    <text x="15" y="94" font-size="11" fill="#334155">• customer_id_web (Natural Key S1)</text>
    <text x="15" y="112" font-size="11" fill="#334155">• member_no (Natural Key S2)</text>
    <text x="15" y="130" font-size="11" fill="#334155">• mpl_buyer_hash (Natural Key S3)</text>
    <text x="15" y="148" font-size="11" fill="#334155">• phone_norm (E.164: +62...)</text>
    <text x="15" y="166" font-size="11" fill="#334155">• nama_pelanggan, gender</text>
    <text x="15" y="184" font-size="11" fill="#334155">• kota_baku, provinsi (ref_kota)</text>
    <text x="15" y="202" font-size="11" fill="#334155">• tgl_daftar_web, tgl_join_member</text>
    <rect x="15" y="214" width="260" height="34" rx="4" fill="#fffbeb"/>
    <text x="145" y="228" text-anchor="middle" font-size="9.5" font-weight="600" fill="#92400e">Identity Resolution: Match Web &amp; Store</text>
    <text x="145" y="241" text-anchor="middle" font-size="9.5" font-weight="500" fill="#92400e">via Nomor Telepon Standar</text>
  </g>

  <!-- ==================== 5. DIM_TOKO_KANAL (Bottom Left) ==================== -->
  <g transform="translate(50, 520)" filter="url(#shadow)">
    <rect width="270" height="230" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 260 0 Q 270 0 270 10 L 270 36 L 0 36 Z" fill="url(#dimGrad)"/>
    <text x="135" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_toko_kanal</text>
    <text x="15" y="58" font-size="11.5" font-weight="700" fill="#0f766e">PK | toko_kanal_key (INT AUTO)</text>
    <text x="15" y="78" font-size="11" fill="#334155">• kode_toko_kanal (TS01..42, WEB, MPL)</text>
    <text x="15" y="96" font-size="11" fill="#334155">• nama_toko_kanal</text>
    <text x="15" y="114" font-size="11" font-weight="600" fill="#0f172a">• kanal (Toko Fisik / Situs Web / Marketplace)</text>
    <text x="15" y="132" font-size="11" fill="#334155">• platform (Offline / Magento / Shopee / dll)</text>
    <text x="15" y="150" font-size="11" fill="#334155">• kota_baku, provinsi (ref_kota)</text>
    <text x="15" y="168" font-size="11" fill="#334155">• format_toko, sistem_sumber</text>
    <rect x="15" y="184" width="240" height="34" rx="4" fill="#f0fdf4"/>
    <text x="135" y="198" text-anchor="middle" font-size="9.5" font-weight="600" fill="#166534">Konsolidasi 42 Toko POS S2,</text>
    <text x="135" y="211" text-anchor="middle" font-size="9.5" font-weight="500" fill="#166534">1 Web S1, dan 2 Toko MPL S3</text>
  </g>

  <!-- ==================== 6. DIM_KAMPANYE (Bottom Center) ==================== -->
  <g transform="translate(480, 725)" filter="url(#shadow)">
    <rect width="320" height="135" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 310 0 Q 320 0 320 10 L 320 32 L 0 32 Z" fill="url(#dimGrad)"/>
    <text x="160" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_kampanye</text>
    <text x="15" y="52" font-size="11.5" font-weight="700" fill="#0f766e">PK | kampanye_key (INT AUTO)</text>
    <text x="15" y="70" font-size="11" fill="#334155">• kode_promo, nama_kampanye</text>
    <text x="15" y="88" font-size="11" fill="#334155">• jenis_promo, kanal_target</text>
    <text x="15" y="106" font-size="11" fill="#334155">• tgl_mulai, tgl_selesai, target_diskon_persen</text>
    <text x="15" y="124" font-size="10.5" fill="#64748b">SK Default: -1 (Tanpa Promo)</text>
  </g>

  <!-- ==================== 7. DIM_METODE_BAYAR (Bottom Right) ==================== -->
  <g transform="translate(950, 620)" filter="url(#shadow)">
    <rect width="270" height="140" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
    <path d="M 0 10 Q 0 0 10 0 L 260 0 Q 270 0 270 10 L 270 32 L 0 32 Z" fill="url(#dimGrad)"/>
    <text x="135" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">dim_metode_bayar</text>
    <text x="15" y="52" font-size="11.5" font-weight="700" fill="#0f766e">PK | metode_bayar_key (INT AUTO)</text>
    <text x="15" y="72" font-size="11" fill="#334155">• metode_bayar (CASH, QRIS, CC, SPLIT, dll)</text>
    <text x="15" y="90" font-size="11" fill="#334155">• kelompok_bayar (TUNAI, DIGITAL, KARTU, dll)</text>
    <text x="15" y="112" font-size="10.5" fill="#64748b">Menampung agregasi multi-metode POS (SPLIT)</text>
  </g>

</svg>
"""

with open(r"g:\My Drive\File Kuliah\Semester 7\data-warehouse\assignment\tugas kelompok\Data-20261013T041524Z-1-001\NRG_DW\star_schema_diagram.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("SVG star schema diagram created successfully.")
