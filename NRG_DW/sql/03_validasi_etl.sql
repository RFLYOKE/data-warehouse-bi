-- =====================================================================
-- TUGAS KELOMPOK 4 - PENGEMBANGAN DATA WAREHOUSE
-- STUDI KASUS: NUSANTARA RETAIL GROUP (NRG)
-- 03_validasi_etl.sql - Skrip Validasi dan Rekonsiliasi Hasil ETL
-- =====================================================================
USE nrg_dw;

-- 1. Rekonsiliasi Jumlah Baris per Sistem Sumber ke Tabel Fakta
SELECT 
    '1. Rekonsiliasi Sumber vs Fakta' AS pengujian,
    sumber_sistem,
    COUNT(*) AS total_baris_fakta,
    SUM(qty) AS total_unit,
    ROUND(SUM(penjualan_kotor_excl), 2) AS penjualan_kotor,
    ROUND(SUM(diskon_excl_ppn), 2) AS diskon,
    ROUND(SUM(penjualan_bersih_excl), 2) AS penjualan_bersih,
    ROUND(SUM(harga_pokok_total), 2) AS total_hpp,
    ROUND(SUM(fee_komisi + fee_layanan), 2) AS total_fees,
    ROUND(SUM(margin_kotor), 2) AS margin_kotor,
    ROUND(SUM(margin_kotor) / NULLIF(SUM(penjualan_bersih_excl), 0) * 100, 2) AS margin_pct
FROM fact_penjualan
GROUP BY sumber_sistem;

-- 2. Audit Kualitas Data S5 (Kampanye Marketing Gagal Validasi)
SELECT 
    '2. Audit S5 Error' AS pengujian,
    kode_promo,
    nama_kampanye,
    target_diskon_persen,
    alasan_error,
    waktu_etl
FROM err_s5_kampanye;

-- 3. Audit Transaksi VOID S2 (Dibuang dari Tabel Fakta)
SELECT 
    '3. Audit S2 VOID' AS pengujian,
    COUNT(*) AS total_transaksi_void_dibuang
FROM rej_s2_void;

-- 4. Validasi Penanganan Late-Arriving Dimension (ORD-9999)
SELECT 
    '4. Late Arriving Dimension' AS pengujian,
    fp.sumber_sistem,
    fp.no_transaksi,
    fp.no_baris,
    dp.material_no,
    dp.nama_produk,
    dp.status_erp,
    dp.is_inferred,
    fp.penjualan_bersih_excl,
    fp.harga_pokok_total,
    fp.margin_kotor
FROM fact_penjualan fp
JOIN dim_produk dp ON dp.produk_key = fp.produk_key
WHERE fp.no_transaksi = 'ORD-9999';

-- 5. Rekonsiliasi Pelanggan (Web vs Member vs Omnichannel)
SELECT 
    '5. Rekonsiliasi Pelanggan' AS pengujian,
    tipe_pelanggan,
    COUNT(*) AS jumlah_dimensi,
    COUNT(DISTINCT phone_norm) AS nomor_hp_unik,
    SUM(CASE WHEN is_web_customer = 'Y' THEN 1 ELSE 0 END) AS web_customers,
    SUM(CASE WHEN is_member_toko = 'Y' THEN 1 ELSE 0 END) AS member_toko
FROM dim_pelanggan
GROUP BY tipe_pelanggan;

-- 6. Pengecekan Integritas Referensial (Tidak Boleh Ada Baris Yatim Piatu)
SELECT 
    '6. Foreign Key Orphan Check' AS pengujian,
    SUM(CASE WHEN dt.tanggal_key IS NULL THEN 1 ELSE 0 END) AS orphan_tanggal,
    SUM(CASE WHEN dp.produk_key IS NULL THEN 1 ELSE 0 END) AS orphan_produk,
    SUM(CASE WHEN dpl.pelanggan_key IS NULL THEN 1 ELSE 0 END) AS orphan_pelanggan,
    SUM(CASE WHEN dtk.toko_kanal_key IS NULL THEN 1 ELSE 0 END) AS orphan_toko_kanal,
    SUM(CASE WHEN dk.kampanye_key IS NULL THEN 1 ELSE 0 END) AS orphan_kampanye,
    SUM(CASE WHEN dmb.metode_bayar_key IS NULL THEN 1 ELSE 0 END) AS orphan_metode_bayar
FROM fact_penjualan fp
LEFT JOIN dim_tanggal dt       ON dt.tanggal_key = fp.tanggal_key
LEFT JOIN dim_produk dp        ON dp.produk_key = fp.produk_key
LEFT JOIN dim_pelanggan dpl    ON dpl.pelanggan_key = fp.pelanggan_key
LEFT JOIN dim_toko_kanal dtk   ON dtk.toko_kanal_key = fp.toko_kanal_key
LEFT JOIN dim_kampanye dk      ON dk.kampanye_key = fp.kampanye_key
LEFT JOIN dim_metode_bayar dmb ON dmb.metode_bayar_key = fp.metode_bayar_key;
