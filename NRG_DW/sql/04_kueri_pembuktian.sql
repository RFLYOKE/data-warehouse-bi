-- =====================================================================
-- TUGAS KELOMPOK 4 - PENGEMBANGAN DATA WAREHOUSE
-- STUDI KASUS: NUSANTARA RETAIL GROUP (NRG)
-- 04_kueri_pembuktian.sql - 4 Kueri SQL untuk Menjawab Pertanyaan Bisnis
-- =====================================================================
USE nrg_dw;

-- =====================================================================
-- PERTANYAAN 1:
-- Berapa margin kotor per sub-kategori produk per kanal, dibandingkan
-- dengan kuartal yang sama pada tahun lalu (Year-over-Year per Kuartal)?
-- =====================================================================
SELECT 
    f.sub_kategori,
    f.kanal,
    f.tahun_kuartal,
    f.penjualan_bersih,
    f.margin_kotor,
    ROUND(f.margin_kotor / NULLIF(f.penjualan_bersih, 0) * 100, 2) AS margin_pct,
    f.margin_kotor_ly AS margin_kotor_tahun_lalu,
    ROUND((f.margin_kotor - f.margin_kotor_ly) / NULLIF(ABS(f.margin_kotor_ly), 0) * 100, 2) AS yoy_growth_margin_pct
FROM (
    SELECT 
        dp.sub_kategori,
        dtk.kanal,
        dt.tahun_kuartal,
        dt.tahun,
        dt.kuartal,
        ROUND(SUM(fp.penjualan_bersih_excl), 2) AS penjualan_bersih,
        ROUND(SUM(fp.margin_kotor), 2) AS margin_kotor,
        LAG(ROUND(SUM(fp.margin_kotor), 2), 1) OVER (
            PARTITION BY dp.sub_kategori, dtk.kanal, dt.kuartal 
            ORDER BY dt.tahun
        ) AS margin_kotor_ly
    FROM fact_penjualan fp
    JOIN dim_tanggal dt       ON dt.tanggal_key = fp.tanggal_key
    JOIN dim_produk dp        ON dp.produk_key = fp.produk_key
    JOIN dim_toko_kanal dtk   ON dtk.toko_kanal_key = fp.toko_kanal_key
    GROUP BY dp.sub_kategori, dtk.kanal, dt.tahun_kuartal, dt.tahun, dt.kuartal
) f
ORDER BY f.sub_kategori, f.kanal, f.tahun_kuartal;


-- =====================================================================
-- PERTANYAAN 2:
-- Apakah pelanggan yang berbelanja secara online adalah orang yang sama
-- dengan pemegang kartu member di toko fisik?
-- (Identifikasi Pelanggan Omnichannel via Pencocokan Nomor HP Ternormalisasi)
-- =====================================================================
-- Bagian 2A: Ringkasan Populasi dan Irisan Pelanggan
SELECT 
    COUNT(CASE WHEN is_web_customer = 'Y' THEN 1 END) AS total_pelanggan_web,
    COUNT(CASE WHEN is_member_toko = 'Y' THEN 1 END) AS total_member_toko_fisik,
    COUNT(CASE WHEN tipe_pelanggan = 'OMNICHANNEL' THEN 1 END) AS jumlah_pelanggan_omnichannel,
    ROUND(COUNT(CASE WHEN tipe_pelanggan = 'OMNICHANNEL' THEN 1 END) * 100.0 / 
          COUNT(CASE WHEN is_web_customer = 'Y' THEN 1 END), 2) AS pct_pelanggan_web_yang_juga_member,
    ROUND(COUNT(CASE WHEN tipe_pelanggan = 'OMNICHANNEL' THEN 1 END) * 100.0 / 
          COUNT(CASE WHEN is_member_toko = 'Y' THEN 1 END), 2) AS pct_member_yang_juga_pelanggan_web
FROM dim_pelanggan
WHERE pelanggan_key > 0;

-- Bagian 2B: Perbandingan Perilaku Belanja Pelanggan Omnichannel vs Single-Channel
SELECT 
    dp.tipe_pelanggan,
    COUNT(DISTINCT dp.pelanggan_key) AS jumlah_pelanggan,
    COUNT(DISTINCT fp.no_transaksi) AS total_transaksi,
    SUM(fp.qty) AS total_unit_terjual,
    ROUND(SUM(fp.penjualan_bersih_excl), 2) AS total_belanja_bersih,
    ROUND(SUM(fp.margin_kotor), 2) AS total_margin_kotor,
    ROUND(SUM(fp.penjualan_bersih_excl) / COUNT(DISTINCT dp.pelanggan_key), 2) AS belanja_rata2_per_pelanggan,
    ROUND(COUNT(DISTINCT fp.no_transaksi) / COUNT(DISTINCT dp.pelanggan_key), 2) AS frekuensi_belanja_rata2
FROM dim_pelanggan dp
JOIN fact_penjualan fp ON fp.pelanggan_key = dp.pelanggan_key
WHERE dp.pelanggan_key > 0
GROUP BY dp.tipe_pelanggan
ORDER BY belanja_rata2_per_pelanggan DESC;


-- =====================================================================
-- PERTANYAAN 3:
-- Kampanye diskon mana yang berhasil menaikkan volume penjualan tanpa
-- menggerus margin? (Analisis Efektivitas Kampanye Promosi)
-- =====================================================================
SELECT 
    dk.kode_promo,
    dk.nama_kampanye,
    dk.jenis_promo,
    dk.kanal_target,
    dk.tgl_mulai,
    dk.tgl_selesai,
    dk.target_diskon_persen,
    COUNT(DISTINCT fp.no_transaksi) AS jumlah_transaksi,
    SUM(fp.qty) AS total_volume_terjual,
    ROUND(SUM(fp.penjualan_kotor_excl), 2) AS penjualan_kotor,
    ROUND(SUM(fp.diskon_excl_ppn), 2) AS total_diskon_diberikan,
    ROUND(SUM(fp.penjualan_bersih_excl), 2) AS penjualan_bersih,
    ROUND(SUM(fp.margin_kotor), 2) AS total_margin_kotor,
    ROUND(SUM(fp.margin_kotor) / NULLIF(SUM(fp.penjualan_bersih_excl), 0) * 100, 2) AS margin_pct,
    ROUND(SUM(fp.diskon_excl_ppn) / NULLIF(SUM(fp.penjualan_kotor_excl), 0) * 100, 2) AS realisasi_diskon_pct,
    CASE 
        WHEN SUM(fp.margin_kotor) / NULLIF(SUM(fp.penjualan_bersih_excl), 0) >= 0.20 
             AND SUM(fp.qty) >= 200 THEN 'Sangat Berhasil (Volume Tinggi, Margin Sehat >= 20%)'
        WHEN SUM(fp.margin_kotor) / NULLIF(SUM(fp.penjualan_bersih_excl), 0) >= 0.20 THEN 'Berhasil (Margin Sehat, Volume Moderat)'
        WHEN SUM(fp.margin_kotor) / NULLIF(SUM(fp.penjualan_bersih_excl), 0) >= 0.15 THEN 'Cukup (Margin Moderat 15-20%)'
        ELSE 'Kurang Efektif (Margin Tergerus < 15%)'
    END AS evaluasi_efektivitas
FROM fact_penjualan fp
JOIN dim_kampanye dk ON dk.kampanye_key = fp.kampanye_key
WHERE dk.kampanye_key > 0
GROUP BY 
    dk.kode_promo, dk.nama_kampanye, dk.jenis_promo, dk.kanal_target,
    dk.tgl_mulai, dk.tgl_selesai, dk.target_diskon_persen
ORDER BY total_volume_terjual DESC, total_margin_kotor DESC;


-- =====================================================================
-- PERTANYAAN 4:
-- Produk apa saja yang volume penjualannya tinggi di marketplace tetapi
-- rendah di toko fisik dan web, sehingga menjadi kandidat pemindahan
-- alokasi stok ke marketplace?
-- =====================================================================
WITH produk_per_kanal AS (
    SELECT 
        dp.material_no,
        dp.nama_produk,
        dp.brand,
        dp.kategori,
        dp.sub_kategori,
        SUM(CASE WHEN dtk.kanal = 'Marketplace' THEN fp.qty ELSE 0 END) AS qty_marketplace,
        SUM(CASE WHEN dtk.kanal = 'Toko Fisik'  THEN fp.qty ELSE 0 END) AS qty_toko_fisik,
        SUM(CASE WHEN dtk.kanal = 'Situs Web'   THEN fp.qty ELSE 0 END) AS qty_situs_web,
        SUM(CASE WHEN dtk.kanal IN ('Toko Fisik', 'Situs Web') THEN fp.qty ELSE 0 END) AS qty_non_marketplace,
        SUM(fp.qty) AS total_qty_semua_kanal,
        ROUND(SUM(CASE WHEN dtk.kanal = 'Marketplace' THEN fp.penjualan_bersih_excl ELSE 0 END), 2) AS omset_marketplace,
        ROUND(SUM(CASE WHEN dtk.kanal = 'Marketplace' THEN fp.margin_kotor ELSE 0 END), 2) AS margin_marketplace
    FROM fact_penjualan fp
    JOIN dim_produk dp      ON dp.produk_key = fp.produk_key
    JOIN dim_toko_kanal dtk ON dtk.toko_kanal_key = fp.toko_kanal_key
    GROUP BY dp.material_no, dp.nama_produk, dp.brand, dp.kategori, dp.sub_kategori
)
SELECT 
    material_no,
    nama_produk,
    brand,
    kategori,
    sub_kategori,
    qty_marketplace,
    qty_toko_fisik,
    qty_situs_web,
    qty_non_marketplace,
    total_qty_semua_kanal,
    ROUND(qty_marketplace * 100.0 / NULLIF(total_qty_semua_kanal, 0), 2) AS pangsa_volume_marketplace_pct,
    ROUND(qty_marketplace / NULLIF(qty_non_marketplace, 0), 2) AS rasio_mpl_vs_non_mpl,
    omset_marketplace,
    margin_marketplace,
    CASE 
        WHEN qty_marketplace > qty_non_marketplace AND (qty_marketplace * 100.0 / total_qty_semua_kanal) >= 60.0 
             THEN 'PRIORITAS 1: Pindahkan Stok Utama (Dominan Marketplace >= 60%)'
        WHEN qty_marketplace > qty_non_marketplace 
             THEN 'PRIORITAS 2: Tingkatkan Alokasi Stok Marketplace (MPL > Non-MPL)'
        ELSE 'Stok Normal / Seimbang'
    END AS rekomendasi_alokasi_stok
FROM produk_per_kanal
WHERE qty_marketplace > 0
ORDER BY rasio_mpl_vs_non_mpl DESC, qty_marketplace DESC;
