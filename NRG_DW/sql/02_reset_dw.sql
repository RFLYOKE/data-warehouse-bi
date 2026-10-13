-- Dijalankan otomatis oleh Job J_NRG_DW_Main (langkah pertama) agar pipeline idempotent.
-- Urutan: fakta -> dimensi -> staging. Baris "unknown member" (key negatif) dimasukkan ulang.
DELETE FROM fact_penjualan;
DELETE FROM dim_produk;
DELETE FROM dim_pemasok;
DELETE FROM dim_pelanggan;
DELETE FROM dim_toko_kanal;
DELETE FROM dim_kampanye;
DELETE FROM dim_metode_bayar;
DELETE FROM dim_tanggal;

DELETE FROM stg_ref_kota;
DELETE FROM stg_erp_pemasok;
DELETE FROM stg_erp_produk;
DELETE FROM stg_s5_kampanye;
DELETE FROM err_s5_kampanye;
DELETE FROM stg_s2_store;
DELETE FROM stg_s2_member;
DELETE FROM stg_s2_trx_header;
DELETE FROM rej_s2_void;
DELETE FROM stg_s2_trx_line;
DELETE FROM stg_s2_trx_payment;
DELETE FROM stg_s1_customer;
DELETE FROM stg_s1_order_line;
DELETE FROM stg_s3_inv_item;
DELETE FROM map_produk;

-- Unknown / not-applicable members (surrogate key negatif)
INSERT INTO dim_pelanggan (pelanggan_key, tipe_pelanggan, nama_pelanggan, is_web_customer, is_member_toko)
VALUES (-1, 'TIDAK_DIKENAL', 'Pelanggan tidak teridentifikasi (walk-in / non-member)', 'N', 'N');

INSERT INTO dim_kampanye (kampanye_key, kode_promo, nama_kampanye, jenis_promo, kanal_target, tgl_mulai, tgl_selesai, status_validasi)
VALUES (-1, 'NONE', 'Tanpa kampanye', 'N/A', 'N/A', '1900-01-01', '9999-12-31', 'N/A'),
       (-2, 'INVALID', 'Kampanye gagal validasi S5 (lihat err_s5_kampanye)', 'N/A', 'N/A', '1900-01-01', '9999-12-31', 'GAGAL');

INSERT INTO dim_metode_bayar (metode_bayar_key, metode_bayar, kelompok_bayar)
VALUES (-1, 'TIDAK DIKETAHUI', 'Tidak diketahui');
