-- =====================================================================
-- NRG DATA WAREHOUSE  -  DDL (MySQL 8.0)
-- Kelompok 4 - Tugas Pengembangan Data Warehouse
-- Jalankan SEKALI dari kondisi kosong:  mysql -uroot < 01_ddl_dw.sql
-- =====================================================================
DROP DATABASE IF EXISTS nrg_dw;
CREATE DATABASE nrg_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nrg_dw;

-- ---------------------------------------------------------------------
-- A. STAGING / REFERENSI  (diisi oleh Transformation T01 - T06)
-- ---------------------------------------------------------------------
CREATE TABLE stg_ref_kota (
    alias_upper   VARCHAR(60) PRIMARY KEY,
    kota_baku     VARCHAR(60) NOT NULL
);

CREATE TABLE stg_erp_pemasok (
    supplier_id    VARCHAR(20) PRIMARY KEY,
    nama_supplier  VARCHAR(100),
    kota           VARCHAR(60),
    kontak         VARCHAR(30)
);

CREATE TABLE stg_erp_produk (               -- riwayat harga pokok (1 baris = 1 versi)
    material_no    VARCHAR(20) NOT NULL,
    nama_produk    VARCHAR(150),
    brand          VARCHAR(60),
    kategori       VARCHAR(60),
    sub_kategori   VARCHAR(60),
    harga_pokok    DECIMAL(18,2),
    supplier       VARCHAR(100),
    status         VARCHAR(15),
    berlaku_sejak  DATE NOT NULL,
    PRIMARY KEY (material_no, berlaku_sejak)
);

CREATE TABLE stg_s5_kampanye (              -- hanya baris lolos validasi, sudah dibersihkan & dedup
    kode_promo           VARCHAR(30) NOT NULL,
    nama_kampanye        VARCHAR(100),
    jenis_promo          VARCHAR(30),
    kanal                VARCHAR(30),
    tgl_mulai            DATE NOT NULL,
    tgl_selesai          DATE,
    target_diskon_persen DECIMAL(6,2),
    pic                  VARCHAR(60),
    PRIMARY KEY (kode_promo, tgl_mulai)
);

CREATE TABLE err_s5_kampanye (              -- baris gagal validasi (jejak audit)
    kode_promo           VARCHAR(60),
    nama_kampanye        VARCHAR(100),
    jenis_promo          VARCHAR(60),
    kanal                VARCHAR(60),
    tgl_mulai            VARCHAR(30),
    tgl_selesai          VARCHAR(30),
    target_diskon_persen VARCHAR(60),
    pic                  VARCHAR(60),
    alasan_error         VARCHAR(200),
    waktu_etl            DATETIME
);

CREATE TABLE stg_s2_store (
    store_code   VARCHAR(10) PRIMARY KEY,
    store_name   VARCHAR(100),
    city_raw     VARCHAR(60),
    kota_baku    VARCHAR(60),
    province     VARCHAR(60),
    format_toko  VARCHAR(30),
    opened_at    DATE
);

CREATE TABLE stg_s2_member (
    member_no    VARCHAR(20) PRIMARY KEY,
    member_name  VARCHAR(120),
    hp_raw       VARCHAR(30),
    phone_norm   VARCHAR(20),
    kota_raw     VARCHAR(60),
    kota_baku    VARCHAR(60),
    join_date    DATE,
    KEY ix_member_phone (phone_norm)
);

CREATE TABLE stg_s2_trx_header (            -- hanya status NORMAL
    trx_no        VARCHAR(30) PRIMARY KEY,
    store_code    VARCHAR(10),
    cashier_id    VARCHAR(10),
    member_no     VARCHAR(20),
    trx_date      DATE,
    payment_type  VARCHAR(10),
    status        VARCHAR(10)
);

CREATE TABLE rej_s2_void (                  -- transaksi VOID yang dibuang (jejak audit)
    trx_no        VARCHAR(30),
    store_code    VARCHAR(10),
    trx_date      DATE,
    payment_type  VARCHAR(10),
    status        VARCHAR(10),
    waktu_etl     DATETIME
);

CREATE TABLE stg_s2_trx_line (
    trx_no           VARCHAR(30) NOT NULL,
    line_seq         INT NOT NULL,
    item_code        VARCHAR(20),
    qty              INT,
    unit_price_excl  DECIMAL(18,2),
    disc_pct         DECIMAL(6,2),
    PRIMARY KEY (trx_no, line_seq)
);

CREATE TABLE stg_s2_trx_payment (           -- agregasi pembayaran per transaksi (SPLIT = >1 baris)
    trx_no           VARCHAR(30) PRIMARY KEY,
    jml_baris_bayar  INT,
    total_bayar      DECIMAL(18,2),
    is_split         CHAR(1)
);

CREATE TABLE stg_s1_customer (
    customer_id    INT PRIMARY KEY,
    full_name      VARCHAR(120),
    email          VARCHAR(120),
    phone_raw      VARCHAR(30),
    phone_norm     VARCHAR(20),
    gender         CHAR(1),
    birth_date     DATE,
    registered_at  DATETIME,
    kota_raw       VARCHAR(60),
    kota_baku      VARCHAR(60),
    provinsi       VARCHAR(60),
    KEY ix_cust_phone (phone_norm)
);

CREATE TABLE stg_s1_order_line (
    order_id          VARCHAR(20) NOT NULL,
    line_no           INT NOT NULL,
    order_ts          DATETIME,                 -- sudah WIB
    status            VARCHAR(20),
    customer_id       INT,
    voucher_id        INT,
    promo_code        VARCHAR(30),
    voucher_valid_from DATE,
    payment_method    VARCHAR(20),
    sku               VARCHAR(40),
    material_no       VARCHAR(40),              -- hasil pemetaan ke master S4
    product_name      VARCHAR(150),
    brand             VARCHAR(60),
    category_name     VARCHAR(60),
    parent_category   VARCHAR(60),
    qty               INT,
    unit_price_incl   DECIMAL(18,2),
    disc_amount_incl  DECIMAL(18,2),
    unit_price_excl   DECIMAL(18,2),
    disc_excl         DECIMAL(18,2),
    qty_retur         INT,
    refund_excl       DECIMAL(18,2),
    PRIMARY KEY (order_id, line_no)
);

CREATE TABLE stg_s3_inv_item (
    invoice             VARCHAR(40) NOT NULL,
    seller_sku          VARCHAR(30) NOT NULL,
    channel             VARCHAR(20),
    paid_at_utc         DATETIME,
    paid_at_wib         DATETIME,
    buyer_hash          VARCHAR(20),
    buyer_city          VARCHAR(60),
    kota_baku           VARCHAR(60),
    qty                 INT,
    price_incl          DECIMAL(18,2),
    voucher_incl        DECIMAL(18,2),
    unit_price_excl     DECIMAL(18,2),
    voucher_excl        DECIMAL(18,2),
    gross_line_incl     DECIMAL(18,2),
    commission_invoice  DECIMAL(18,2),
    service_invoice     DECIMAL(18,2),
    fee_komisi_alokasi  DECIMAL(18,2),
    fee_layanan_alokasi DECIMAL(18,2),
    material_no         VARCHAR(20),
    diambil_pada        DATETIME,
    PRIMARY KEY (invoice, seller_sku)
);

CREATE TABLE map_produk (                      -- tabel pemetaan produk lintas sumber -> material_no
    sumber        VARCHAR(10) NOT NULL,
    kode_sumber   VARCHAR(40) NOT NULL,
    material_no   VARCHAR(40) NOT NULL,
    aturan        VARCHAR(80),
    terdaftar_erp CHAR(1),
    PRIMARY KEY (sumber, kode_sumber)
);

-- ---------------------------------------------------------------------
-- B. DIMENSI
-- ---------------------------------------------------------------------
CREATE TABLE dim_tanggal (
    tanggal_key   INT PRIMARY KEY,            -- yyyymmdd
    tanggal       DATE NOT NULL,
    hari          TINYINT,
    nama_hari     VARCHAR(10),
    minggu_ke     TINYINT,
    bulan         TINYINT,
    nama_bulan    VARCHAR(12),
    kuartal       TINYINT,
    tahun         SMALLINT,
    tahun_kuartal VARCHAR(8),
    is_weekend    CHAR(1)
);

CREATE TABLE dim_pemasok (
    pemasok_key    INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id    VARCHAR(20),
    nama_supplier  VARCHAR(100),
    kota           VARCHAR(60),
    kontak         VARCHAR(30)
);

CREATE TABLE dim_produk (                     -- SCD Tipe 2 pada harga pokok (versi ERP)
    produk_key         INT AUTO_INCREMENT PRIMARY KEY,
    material_no        VARCHAR(40) NOT NULL,
    nama_produk        VARCHAR(150),
    brand              VARCHAR(60),
    kategori           VARCHAR(60),
    sub_kategori       VARCHAR(60),
    pemasok_key        INT,
    nama_pemasok       VARCHAR(100),
    status_erp         VARCHAR(15),
    harga_pokok        DECIMAL(18,2),         -- NULL untuk late arriving (belum ada di ERP)
    berlaku_sejak      DATE,
    tgl_efektif_awal   DATE NOT NULL,
    tgl_efektif_akhir  DATE NOT NULL,
    is_current         CHAR(1),
    is_inferred        CHAR(1) DEFAULT 'N',   -- Y = baris dibuat otomatis (late arriving dimension)
    KEY ix_produk_nk (material_no, tgl_efektif_awal, tgl_efektif_akhir),
    CONSTRAINT fk_produk_pemasok FOREIGN KEY (pemasok_key) REFERENCES dim_pemasok(pemasok_key)
);

CREATE TABLE dim_pelanggan (
    pelanggan_key    INT AUTO_INCREMENT PRIMARY KEY,
    tipe_pelanggan   VARCHAR(15) NOT NULL,    -- OMNICHANNEL | WEB_ONLY | MEMBER_TOKO | MARKETPLACE | TIDAK_DIKENAL
    customer_id_web  INT NULL,
    member_no        VARCHAR(20) NULL,
    mpl_buyer_hash   VARCHAR(20) NULL,
    phone_norm       VARCHAR(20),
    nama_pelanggan   VARCHAR(120),
    gender           CHAR(1),
    kota_baku        VARCHAR(60),
    provinsi         VARCHAR(60),
    tgl_daftar_web   DATETIME,
    tgl_join_member  DATE,
    is_web_customer  CHAR(1),
    is_member_toko   CHAR(1),
    KEY ix_pel_web (customer_id_web),
    KEY ix_pel_mem (member_no),
    KEY ix_pel_hash (mpl_buyer_hash)
);

CREATE TABLE dim_toko_kanal (
    toko_kanal_key   INT AUTO_INCREMENT PRIMARY KEY,
    kode_toko_kanal  VARCHAR(10) NOT NULL UNIQUE,   -- TS01.. | WEB | MPL_A | MPL_B
    nama_toko_kanal  VARCHAR(100),
    kanal            VARCHAR(20),                   -- Toko Fisik | Situs Web | Marketplace
    platform         VARCHAR(30),
    kota_baku        VARCHAR(60),
    provinsi         VARCHAR(60),
    format_toko      VARCHAR(30),
    sistem_sumber    VARCHAR(10)
);

CREATE TABLE dim_kampanye (
    kampanye_key         INT AUTO_INCREMENT PRIMARY KEY,
    kode_promo           VARCHAR(30),
    nama_kampanye        VARCHAR(100),
    jenis_promo          VARCHAR(30),
    kanal_target         VARCHAR(30),
    tgl_mulai            DATE,
    tgl_selesai          DATE,
    target_diskon_persen DECIMAL(6,2),
    pic                  VARCHAR(60),
    status_validasi      VARCHAR(20),
    UNIQUE KEY uq_kampanye (kode_promo, tgl_mulai)
);

CREATE TABLE dim_metode_bayar (
    metode_bayar_key  INT AUTO_INCREMENT PRIMARY KEY,
    metode_bayar      VARCHAR(30) NOT NULL UNIQUE,
    kelompok_bayar    VARCHAR(20)
);

-- ---------------------------------------------------------------------
-- C. TABEL FAKTA  (grain: 1 baris per item transaksi)
-- ---------------------------------------------------------------------
CREATE TABLE fact_penjualan (
    fact_key                BIGINT AUTO_INCREMENT PRIMARY KEY,
    sumber_sistem           VARCHAR(10) NOT NULL,      -- S1_WEB | S2_POS | S3_MPL
    no_transaksi            VARCHAR(40) NOT NULL,      -- degenerate: order_id / trx_no / invoice
    no_baris                INT NOT NULL,              -- degenerate: line_no / line_seq / urutan item
    tanggal_key             INT NOT NULL,
    waktu_transaksi_wib     DATETIME NOT NULL,
    produk_key              INT NOT NULL,
    pelanggan_key           INT NOT NULL,
    toko_kanal_key          INT NOT NULL,
    kampanye_key            INT NOT NULL,
    metode_bayar_key        INT NOT NULL,
    qty                     INT NOT NULL,
    harga_satuan_excl_ppn   DECIMAL(18,2) NOT NULL,
    penjualan_kotor_excl    DECIMAL(18,2) NOT NULL,    -- qty x harga satuan
    diskon_excl_ppn         DECIMAL(18,2) NOT NULL,
    penjualan_bersih_excl   DECIMAL(18,2) NOT NULL,    -- kotor - diskon
    harga_pokok_satuan      DECIMAL(18,2) NULL,
    harga_pokok_total       DECIMAL(18,2) NULL,
    fee_komisi              DECIMAL(18,2) NOT NULL DEFAULT 0,
    fee_layanan             DECIMAL(18,2) NOT NULL DEFAULT 0,
    margin_kotor            DECIMAL(18,2) NULL,        -- bersih - HPP - komisi - layanan
    qty_retur               INT NOT NULL DEFAULT 0,
    nilai_retur_excl_ppn    DECIMAL(18,2) NOT NULL DEFAULT 0,
    UNIQUE KEY uq_fact_grain (sumber_sistem, no_transaksi, no_baris),
    KEY ix_fact_tgl (tanggal_key),
    KEY ix_fact_prod (produk_key),
    KEY ix_fact_pel (pelanggan_key),
    KEY ix_fact_tk (toko_kanal_key),
    KEY ix_fact_kamp (kampanye_key),
    CONSTRAINT fk_f_tgl  FOREIGN KEY (tanggal_key)      REFERENCES dim_tanggal(tanggal_key),
    CONSTRAINT fk_f_prod FOREIGN KEY (produk_key)       REFERENCES dim_produk(produk_key),
    CONSTRAINT fk_f_pel  FOREIGN KEY (pelanggan_key)    REFERENCES dim_pelanggan(pelanggan_key),
    CONSTRAINT fk_f_tk   FOREIGN KEY (toko_kanal_key)   REFERENCES dim_toko_kanal(toko_kanal_key),
    CONSTRAINT fk_f_kamp FOREIGN KEY (kampanye_key)     REFERENCES dim_kampanye(kampanye_key),
    CONSTRAINT fk_f_byr  FOREIGN KEY (metode_bayar_key) REFERENCES dim_metode_bayar(metode_bayar_key)
);
