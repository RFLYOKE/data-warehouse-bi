#!/usr/bin/env python3
"""
Generator berkas Pentaho (.ktr / .kjb) untuk pipeline NRG Data Warehouse.

Berkas .ktr/.kjb adalah XML; skrip ini hanya membantu menulisnya secara konsisten.
Hasilnya dapat dibuka dan diedit normal di Spoon.   Jalankan:  python tools/gen_pdi.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pentaho")
os.makedirs(OUT, exist_ok=True)

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(ROOT, "..", "Data")).replace("\\", "/")

PARAMS = [
    ("DATA_DIR", DEFAULT_DATA_DIR, "Folder paket data (berisi S1_ECOM_DB, S2_POS_TOKO, ...)"),
    ("DB_HOST", "localhost", "Host MySQL"),
    ("DB_PORT", "3306", "Port MySQL"),
    ("DB_USER", "root", "User MySQL"),
    ("DB_PASS", "", "Password MySQL"),
    ("DW_DB", "nrg_dw", "Nama database data warehouse"),
    ("ECOM_DB", "nrg_ecom", "Nama database OLTP situs web (S1)"),
]

# ----------------------------------------------------------------- util XML
def cd(s):
    return "<![CDATA[" + s + "]]>"


def params_xml():
    return "<parameters>" + "".join(
        f"<parameter><name>{n}</name><default_value>{d}</default_value><description>{desc}</description></parameter>"
        for n, d, desc in PARAMS) + "</parameters>"


def conn_xml(name, dbvar):
    return f"""<connection><name>{name}</name><server>${{DB_HOST}}</server><type>MYSQL</type><access>Native</access>
<database>${{{dbvar}}}</database><port>${{DB_PORT}}</port><username>${{DB_USER}}</username><password>${{DB_PASS}}</password>
<servername/><data_tablespace/><index_tablespace/><attributes>
<attribute><code>FORCE_IDENTIFIERS_TO_LOWERCASE</code><attribute>N</attribute></attribute>
<attribute><code>FORCE_IDENTIFIERS_TO_UPPERCASE</code><attribute>N</attribute></attribute>
<attribute><code>IS_CLUSTERED</code><attribute>N</attribute></attribute>
<attribute><code>PORT_NUMBER</code><attribute>${{DB_PORT}}</attribute></attribute>
<attribute><code>QUOTE_ALL_FIELDS</code><attribute>N</attribute></attribute>
<attribute><code>SUPPORTS_BOOLEAN_DATA_TYPE</code><attribute>Y</attribute></attribute>
<attribute><code>USE_POOLING</code><attribute>N</attribute></attribute>
<attribute><code>EXTRA_OPTION_MYSQL.useSSL</code><attribute>false</attribute></attribute>
<attribute><code>EXTRA_OPTION_MYSQL.allowPublicKeyRetrieval</code><attribute>true</attribute></attribute>
<attribute><code>EXTRA_OPTION_MYSQL.characterEncoding</code><attribute>UTF-8</attribute></attribute>
<attribute><code>EXTRA_OPTION_MYSQL.connectionCollation</code><attribute>utf8mb4_unicode_ci</attribute></attribute>
</attributes></connection>"""


class Trans:
    def __init__(self, fname, name, desc):
        self.fname, self.name, self.desc = fname, name, desc
        self.steps, self.hops, self.errs = [], [], []

    def add(self, name, type_, body, x, y, distribute="Y"):
        self.steps.append(
            f"""<step><name>{name}</name><type>{type_}</type><description/><distribute>{distribute}</distribute>
<custom_distribution/><copies>1</copies><partitioning><method>none</method><schema_name/></partitioning>
{body}<cluster_schema/><remotesteps><input/><output/></remotesteps>
<GUI><xloc>{x}</xloc><yloc>{y}</yloc><draw>Y</draw></GUI></step>""")
        return name

    def hop(self, a, b):
        self.hops.append((a, b))

    def chain(self, *names):
        for a, b in zip(names, names[1:]):
            self.hop(a, b)

    def save(self):
        hops = "".join(f"<hop><from>{a}</from><to>{b}</to><enabled>Y</enabled></hop>" for a, b in self.hops)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<transformation>
<info><name>{self.name}</name><description>{self.desc}</description><extended_description/><trans_version/>
<trans_type>Normal</trans_type><trans_status>0</trans_status><directory>/</directory>
{params_xml()}
<log><trans-log-table><connection/><schema/><table/><size_limit_lines/><interval/><timeout_days/></trans-log-table></log>
<maxdate><connection/><table/><field/><offset>0.0</offset><maxdiff>0.0</maxdiff></maxdate>
<size_rowset>10000</size_rowset><sleep_time_empty>50</sleep_time_empty><sleep_time_full>50</sleep_time_full>
<unique_connections>N</unique_connections><feedback_shown>Y</feedback_shown><feedback_size>50000</feedback_size>
<using_thread_priorities>Y</using_thread_priorities><shared_objects_file/><capture_step_performance>N</capture_step_performance>
<step_performance_capturing_delay>1000</step_performance_capturing_delay><step_performance_capturing_size_limit>100</step_performance_capturing_size_limit>
<dependencies/><partitionschemas/><slaveservers/><clusterschemas/><created_user>kelompok4</created_user><created_date>2026/10/13 12:00:00.000</created_date>
<modified_user>kelompok4</modified_user><modified_date>2026/10/13 12:00:00.000</modified_date></info>
<notepads/>
{conn_xml("NRG_DW", "DW_DB")}
{conn_xml("NRG_ECOM", "ECOM_DB")}
<order>{hops}</order>
{"".join(self.steps)}
<step_error_handling/>
<slave-step-copy-partition-distribution/><slave_transformation>N</slave_transformation>
</transformation>
"""
        with open(os.path.join(OUT, self.fname), "w", encoding="utf-8") as f:
            f.write(xml)
        print("ditulis", self.fname)


# ----------------------------------------------------------------- step builders
def field_def(name, type_="String", fmt="", length="-1", precision="-1", trim="both"):
    return (f"<field><name>{name}</name><type>{type_}</type><format>{fmt}</format><currency/><decimal/><group/>"
            f"<nullif/><ifnull/><position/><length>{length}</length><precision>{precision}</precision>"
            f"<trim_type>{trim}</trim_type><repeat>N</repeat></field>")


def text_input(t, name, directory, filemask, sep, cols, x, y, with_filename=False):
    fields = "".join(field_def(c) for c in cols)
    body = f"""<accept_filenames>N</accept_filenames><passing_through_fields>N</passing_through_fields><accept_stepname/><accept_field/>
<separator>{sep}</separator><enclosure>"</enclosure><enclosure_breaks>N</enclosure_breaks><escapechar/><header>Y</header>
<nr_headerlines>1</nr_headerlines><footer>N</footer><nr_footerlines>1</nr_footerlines><line_wrapped>N</line_wrapped><nr_wraps>1</nr_wraps>
<layout_paged>N</layout_paged><nr_lines_per_page>80</nr_lines_per_page><nr_lines_doc_header>0</nr_lines_doc_header>
<noempty>Y</noempty><include>{'Y' if with_filename else 'N'}</include><include_field>{'nama_file' if with_filename else ''}</include_field>
<rownum>N</rownum><rownumByFile>N</rownumByFile><rownum_field/><format>mixed</format><encoding>UTF-8</encoding>
<add_to_result_filenames>N</add_to_result_filenames>
<file><name>{directory}</name><filemask>{filemask}</filemask><exclude_filemask/><file_required>Y</file_required><include_subfolders>N</include_subfolders><type>CSV</type><compression>None</compression></file>
<filters/><fields>{fields}</fields><limit>0</limit><error_ignored>N</error_ignored><skip_bad_files>N</skip_bad_files>
<file_error_field/><file_error_message_field/><error_line_skipped>N</error_line_skipped><error_count_field/><error_fields_field/>
<error_text_field/><bad_line_files_destination_directory/><bad_line_files_extension/><error_line_files_destination_directory/>
<error_line_files_extension/><line_number_files_destination_directory/><line_number_files_extension/><date_format_lenient>Y</date_format_lenient>
<date_format_locale>en_US</date_format_locale><shortFileFieldName/><pathFieldName/><hiddenFieldName/><lastModificationTimeFieldName/>
<uriNameFieldName/><rootUriNameFieldName/><extensionFieldName/><sizeFieldName/>"""
    return t.add(name, "TextFileInput", body, x, y)


def json_input(t, name, fields, x, y, directory=None, filemask=None, in_field=None):
    f = "".join(
        f"<field><name>{n}</name><path>{p}</path><type>String</type><format/><currency/><decimal/><group/>"
        f"<length>-1</length><precision>-1</precision><trim_type>none</trim_type><repeat>N</repeat></field>"
        for n, p in fields)
    file_xml = (f"<file><name>{directory}</name><filemask>{filemask}</filemask><exclude_filemask/><file_required>Y</file_required>"
                f"<include_subfolders>N</include_subfolders></file>") if directory else ""
    body = f"""<include>N</include><include_field/><rownum>N</rownum><addresultfile>N</addresultfile><readurl>N</readurl>
<removeSourceField>N</removeSourceField><IsIgnoreEmptyFile>N</IsIgnoreEmptyFile><doNotFailIfNoFile>N</doNotFailIfNoFile>
<ignoreMissingPath>Y</ignoreMissingPath><defaultPathLeafToNull>Y</defaultPathLeafToNull><rownum_field/>
{file_xml}<fields>{f}</fields><limit>0</limit><IsInFields>{'Y' if in_field else 'N'}</IsInFields><IsAFile>N</IsAFile>
<valueField>{in_field or ''}</valueField><shortFileFieldName/><pathFieldName/><hiddenFieldName/><lastModificationTimeFieldName/>
<uriNameFieldName/><rootUriNameFieldName/><extensionFieldName/><sizeFieldName/>"""
    return t.add(name, "JsonInput", body, x, y)


JS_HELPERS = r"""
function T(x) { if (x == null) return null; var s = ("" + x).replace(/^\s+|\s+$/g, ""); return s.length == 0 ? null : s; }
function NUM(x) { var s = T(x); return s == null ? null : parseFloat(s); }
function INT(x) { var s = T(x); return s == null ? null : parseInt(s, 10); }
function R2(x) { return Math.round(x * 100) / 100; }
"""


def js(t, name, code, outs, x, y):
    """outs: list of (nama, tipe) -> field baru yang dihasilkan skrip."""
    fields = "".join(
        f"<field><name>{n}</name><rename>{n}</rename><type>{ty}</type><length>-1</length><precision>-1</precision><replace>N</replace></field>"
        for n, ty in outs)
    body = (f"<compatible>N</compatible><optimizationLevel>9</optimizationLevel><jsScripts><jsScript><jsScript_type>0</jsScript_type>"
            f"<jsScript_name>Script</jsScript_name><jsScript_script>{cd(JS_HELPERS + code)}</jsScript_script></jsScript></jsScripts><fields>{fields}</fields>")
    return t.add(name, "ScriptValueMod", body, x, y)


def table_input(t, name, sql, x, y, conn="NRG_DW", distribute="Y"):
    body = (f"<connection>{conn}</connection><sql>{cd(sql)}</sql><limit>0</limit><lookup/><execute_each_row>N</execute_each_row>"
            f"<variables_active>N</variables_active><lazy_conversion_active>N</lazy_conversion_active>")
    return t.add(name, "TableInput", body, x, y, distribute)


def table_output(t, name, table, mapping, x, y, conn="NRG_DW"):
    flds = "".join(f"<field><column_name>{c}</column_name><stream_name>{s}</stream_name></field>" for c, s in mapping)
    body = (f"<connection>{conn}</connection><schema/><table>{table}</table><commit>1000</commit><truncate>N</truncate>"
            f"<ignore_errors>N</ignore_errors><use_batch>Y</use_batch><specify_fields>Y</specify_fields>"
            f"<partitioning_enabled>N</partitioning_enabled><partitioning_field/><partitioning_daily>N</partitioning_daily>"
            f"<partitioning_monthly>Y</partitioning_monthly><tablename_in_field>N</tablename_in_field><tablename_field/>"
            f"<tablename_in_table>Y</tablename_in_table><return_keys>N</return_keys><return_field/><fields>{flds}</fields>")
    return t.add(name, "TableOutput", body, x, y)


def db_lookup(t, name, table, key_stream, key_table, ret_table, ret_name, x, y, conn="NRG_DW"):
    body = (f"<connection>{conn}</connection><cache>Y</cache><cache_size>0</cache_size><cache_load_all>Y</cache_load_all>"
            f"<lookup><schema/><table>{table}</table><orderby/><fail_on_multiple>N</fail_on_multiple><eat_row_on_failure>N</eat_row_on_failure>"
            f"<key><name>{key_stream}</name><field>{key_table}</field><condition>=</condition><name2/></key>"
            f"<value><name>{ret_table}</name><rename>{ret_name}</rename><default/><type>String</type></value></lookup>")
    return t.add(name, "DBLookup", body, x, y)


def filter_rows(t, name, field, value, true_to, false_to, x, y):
    body = (f"<send_true_to>{true_to}</send_true_to><send_false_to>{false_to}</send_false_to><compare><condition><negated>N</negated>"
            f"<leftvalue>{field}</leftvalue><function>=</function><rightvalue/><value><name>constant</name><type>String</type>"
            f"<text>{value}</text><length>-1</length><precision>-1</precision><isnull>N</isnull><mask/></value></condition></compare>")
    return t.add(name, "FilterRows", body, x, y)


def sort_rows(t, name, keys, x, y):
    """keys: list of (field, ascending_bool)"""
    f = "".join(f"<field><name>{k}</name><ascending>{'Y' if a else 'N'}</ascending><case_sensitive>N</case_sensitive>"
                f"<collator_enabled>N</collator_enabled><collator_strength>0</collator_strength><presorted>N</presorted></field>"
                for k, a in keys)
    body = (f"<directory>%%java.io.tmpdir%%</directory><prefix>out</prefix><sort_size>1000000</sort_size><free_memory/>"
            f"<compress>N</compress><compress_variable/><unique_rows>N</unique_rows><fields>{f}</fields>")
    return t.add(name, "SortRows", body, x, y)


def unique_rows(t, name, keys, x, y, distribute="Y"):
    f = "".join(f"<field><name>{k}</name><case_insensitive>N</case_insensitive></field>" for k in keys)
    body = (f"<count_rows>N</count_rows><count_field/><reject_duplicate_row>N</reject_duplicate_row><error_description/>"
            f"<fields>{f}</fields>")
    return t.add(name, "Unique", body, x, y, distribute)


def group_by(t, name, group_fields, aggs, x, y):
    """aggs: list of (nama_baru, subject, tipe)"""
    g = "".join(f"<field><name>{k}</name></field>" for k in group_fields)
    a = "".join(f"<field><aggregate>{n}</aggregate><subject>{s}</subject><type>{ty}</type><valuefield/></field>" for n, s, ty in aggs)
    body = (f"<all_rows>N</all_rows><ignore_aggregate>N</ignore_aggregate><field_ignore/><directory>%%java.io.tmpdir%%</directory>"
            f"<prefix>grp</prefix><add_linenr>N</add_linenr><linenr_fieldname/><give_back_row>N</give_back_row>"
            f"<group>{g}</group><fields>{a}</fields>")
    return t.add(name, "GroupBy", body, x, y)


def stream_lookup(t, name, from_step, key_main, key_lookup, values, x, y):
    """values: list of (field_lookup, rename, tipe)"""
    v = "".join(f"<value><name>{n}</name><rename>{r}</rename><default/><type>{ty}</type></value>" for n, r, ty in values)
    body = (f"<from>{from_step}</from><input_sorted>N</input_sorted><preserve_memory>Y</preserve_memory><sorted_list>N</sorted_list>"
            f"<integer_pair>N</integer_pair><lookup><key><name>{key_main}</name><field>{key_lookup}</field></key>{v}</lookup>")
    return t.add(name, "StreamLookup", body, x, y)


def dummy(t, name, x, y):
    return t.add(name, "Dummy", "", x, y)


# =====================================================================
# T01  S4 (ERP) + ref_kota
# =====================================================================
def t01():
    t = Trans("T01_stg_s4_erp_ref_kota.ktr", "T01_stg_s4_erp_ref_kota",
              "Ekstrak S4 (produk_master, supplier_master) dan ref_kota.csv ke staging")
    d = "${DATA_DIR}/S4_ERP_MASTER/produk_master.csv"
    text_input(t, "CSV produk_master (S4)", "${DATA_DIR}/S4_ERP_MASTER", "produk_master\\.csv", ",",
               ["material_no", "nama_produk", "brand", "kategori", "sub_kategori", "harga_pokok", "supplier", "status", "berlaku_sejak"], 100, 80)
    js(t, "Bersihkan produk ERP", """
var material_no_c = T(material_no); var nama_c = T(nama_produk); var brand_c = T(brand);
var kategori_c = T(kategori); var sub_c = T(sub_kategori); var supplier_c = T(supplier);
var status_c = T(status) == null ? null : T(status).toUpperCase();
var harga_n = NUM(harga_pokok);
var berlaku_d = str2date(T(berlaku_sejak), "yyyy-MM-dd");
""", [("material_no_c", "String"), ("nama_c", "String"), ("brand_c", "String"), ("kategori_c", "String"), ("sub_c", "String"),
      ("supplier_c", "String"), ("status_c", "String"), ("harga_n", "Number"), ("berlaku_d", "Date")], 340, 80)
    table_output(t, "stg_erp_produk", "stg_erp_produk",
                 [("material_no", "material_no_c"), ("nama_produk", "nama_c"), ("brand", "brand_c"), ("kategori", "kategori_c"),
                  ("sub_kategori", "sub_c"), ("harga_pokok", "harga_n"), ("supplier", "supplier_c"), ("status", "status_c"),
                  ("berlaku_sejak", "berlaku_d")], 580, 80)
    t.chain("CSV produk_master (S4)", "Bersihkan produk ERP", "stg_erp_produk")

    text_input(t, "CSV supplier_master (S4)", "${DATA_DIR}/S4_ERP_MASTER", "supplier_master\\.csv", ",",
               ["supplier_id", "nama_supplier", "kota", "kontak"], 100, 200)
    table_output(t, "stg_erp_pemasok", "stg_erp_pemasok",
                 [("supplier_id", "supplier_id"), ("nama_supplier", "nama_supplier"), ("kota", "kota"), ("kontak", "kontak")], 340, 200)
    t.chain("CSV supplier_master (S4)", "stg_erp_pemasok")

    text_input(t, "CSV ref_kota", "${DATA_DIR}", "ref_kota\\.csv", ",", ["alias", "kota_baku"], 100, 320)
    js(t, "Normalkan alias kota", """
var alias_upper = T(alias) == null ? null : T(alias).toUpperCase().replace(/\\s+/g, " ");
var kota_baku_c = T(kota_baku);
""", [("alias_upper", "String"), ("kota_baku_c", "String")], 340, 320)
    unique_rows_name = None
    sort_rows(t, "Urutkan alias", [("alias_upper", True)], 560, 320)
    unique_rows(t, "Hapus alias ganda", ["alias_upper"], 740, 320)
    table_output(t, "stg_ref_kota", "stg_ref_kota", [("alias_upper", "alias_upper"), ("kota_baku", "kota_baku_c")], 920, 320)
    t.chain("CSV ref_kota", "Normalkan alias kota", "Urutkan alias", "Hapus alias ganda", "stg_ref_kota")
    t.save()


# =====================================================================
# T02  S5 kampanye
# =====================================================================
def t02():
    t = Trans("T02_stg_s5_kampanye.ktr", "T02_stg_s5_kampanye",
              "Ekstrak dan bersihkan kampanye_marketing.csv; baris gagal validasi diarahkan ke err_s5_kampanye")
    text_input(t, "CSV kampanye (S5)", "${DATA_DIR}/S5_MKT_SHEET", "kampanye_marketing\\.csv", ",",
               ["kode_promo", "nama_kampanye", "jenis_promo", "kanal", "tgl_mulai", "tgl_selesai", "target_diskon_persen", "pic"], 80, 160)
    js(t, "Validasi dan normalisasi", """
var status_baris = "OK"; var alasan = ""; 
var kode_norm = null, nama_n = null, jenis_n = null, kanal_n = null, pic_n = null;
var tgl_mulai_d = null, tgl_selesai_d = null, target_n = null;
var waktu_etl = new Date();
if (T(kode_promo) == null && T(nama_kampanye) == null && T(tgl_mulai) == null && T(tgl_selesai) == null && T(target_diskon_persen) == null) {
    status_baris = "KOSONG"; alasan = "Baris kosong";
} else {
    kode_norm = T(kode_promo) == null ? null : T(kode_promo).toUpperCase().replace(/\\s+/g, "");
    nama_n = T(nama_kampanye); jenis_n = T(jenis_promo); kanal_n = T(kanal); pic_n = T(pic);
    var tt = T(target_diskon_persen);
    if (kode_norm == null) { status_baris = "ERROR"; alasan = "kode_promo kosong"; }
    else if (tt == null || !/^[0-9]+(\\.[0-9]+)?$/.test(tt)) {
        status_baris = "ERROR"; alasan = "target_diskon_persen bukan angka: '" + tt + "'";
    } else {
        target_n = parseFloat(tt);
        try { tgl_mulai_d = str2date(T(tgl_mulai), "dd-MM-yyyy"); tgl_selesai_d = str2date(T(tgl_selesai), "dd-MM-yyyy"); }
        catch (e) { status_baris = "ERROR"; alasan = "format tanggal tidak valid"; }
    }
}
""", [("status_baris", "String"), ("alasan", "String"), ("kode_norm", "String"), ("nama_n", "String"), ("jenis_n", "String"),
      ("kanal_n", "String"), ("pic_n", "String"), ("tgl_mulai_d", "Date"), ("tgl_selesai_d", "Date"), ("target_n", "Number"),
      ("waktu_etl", "Date")], 290, 160)
    filter_rows(t, "Baris valid?", "status_baris", "OK", "Urutkan kampanye", "Baris error?", 500, 160)
    filter_rows(t, "Baris error?", "status_baris", "ERROR", "err_s5_kampanye", "Buang baris kosong", 500, 280)
    dummy(t, "Buang baris kosong", 700, 330)
    sort_rows(t, "Urutkan kampanye", [("kode_norm", True), ("tgl_mulai_d", True)], 700, 100)
    unique_rows(t, "Hapus duplikat persis", ["kode_norm", "tgl_mulai_d"], 890, 100)
    table_output(t, "stg_s5_kampanye", "stg_s5_kampanye",
                 [("kode_promo", "kode_norm"), ("nama_kampanye", "nama_n"), ("jenis_promo", "jenis_n"), ("kanal", "kanal_n"),
                  ("tgl_mulai", "tgl_mulai_d"), ("tgl_selesai", "tgl_selesai_d"), ("target_diskon_persen", "target_n"), ("pic", "pic_n")], 1080, 100)
    table_output(t, "err_s5_kampanye", "err_s5_kampanye",
                 [("kode_promo", "kode_promo"), ("nama_kampanye", "nama_kampanye"), ("jenis_promo", "jenis_promo"), ("kanal", "kanal"),
                  ("tgl_mulai", "tgl_mulai"), ("tgl_selesai", "tgl_selesai"), ("target_diskon_persen", "target_diskon_persen"),
                  ("pic", "pic"), ("alasan_error", "alasan"), ("waktu_etl", "waktu_etl")], 700, 240)
    t.chain("CSV kampanye (S5)", "Validasi dan normalisasi", "Baris valid?")
    t.hop("Baris valid?", "Urutkan kampanye"); t.hop("Baris valid?", "Baris error?")
    t.hop("Baris error?", "err_s5_kampanye"); t.hop("Baris error?", "Buang baris kosong")
    t.chain("Urutkan kampanye", "Hapus duplikat persis", "stg_s5_kampanye")
    t.save()


# =====================================================================
# T03  S2 master: store dan member
# =====================================================================
PHONE_JS = """
var d = T(%s) == null ? "" : T(%s).replace(/[^0-9]/g, "");
var phone_norm = null;
if (d.length > 0) {
    if (d.indexOf("62") == 0) phone_norm = d;
    else if (d.charAt(0) == "0") phone_norm = "62" + d.substring(1);
    else phone_norm = "62" + d;
}
"""


def t03():
    t = Trans("T03_stg_s2_master.ktr", "T03_stg_s2_master",
              "Ekstrak master S2: store_master dan member (normalisasi HP + kota baku via ref_kota)")
    text_input(t, "CSV store_master (S2)", "${DATA_DIR}/S2_POS_TOKO", "store_master\\.csv", ",",
               ["store_id", "store_code", "store_name", "city", "province", "format_toko", "opened_at"], 80, 100)
    js(t, "Siapkan toko", """
var city_upper = T(city) == null ? null : T(city).toUpperCase().replace(/\\s+/g, " ");
var opened_d = T(opened_at) == null ? null : str2date(T(opened_at), "yyyy-MM-dd");
""", [("city_upper", "String"), ("opened_d", "Date")], 290, 100)
    db_lookup(t, "Kota baku toko", "stg_ref_kota", "city_upper", "alias_upper", "kota_baku", "kota_lookup", 490, 100)
    js(t, "Kota toko final", """var kota_final = T(kota_lookup) != null ? T(kota_lookup) : T(city);""", [("kota_final", "String")], 690, 100)
    table_output(t, "stg_s2_store", "stg_s2_store",
                 [("store_code", "store_code"), ("store_name", "store_name"), ("city_raw", "city"), ("kota_baku", "kota_final"),
                  ("province", "province"), ("format_toko", "format_toko"), ("opened_at", "opened_d")], 890, 100)
    t.chain("CSV store_master (S2)", "Siapkan toko", "Kota baku toko", "Kota toko final", "stg_s2_store")

    text_input(t, "CSV member (S2)", "${DATA_DIR}/S2_POS_TOKO", "member\\.csv", ";",
               ["member_no", "member_name", "hp", "kota", "join_date"], 80, 260)
    js(t, "Normalkan HP dan kota member", PHONE_JS % ("hp", "hp") + """
var kota_upper = T(kota) == null ? null : T(kota).toUpperCase().replace(/\\s+/g, " ");
var join_d = T(join_date) == null ? null : str2date(T(join_date), "yyyy-MM-dd");
""", [("phone_norm", "String"), ("kota_upper", "String"), ("join_d", "Date")], 290, 260)
    db_lookup(t, "Kota baku member", "stg_ref_kota", "kota_upper", "alias_upper", "kota_baku", "kota_lookup", 490, 260)
    js(t, "Kota member final", """var kota_final = T(kota_lookup) != null ? T(kota_lookup) : T(kota);""", [("kota_final", "String")], 690, 260)
    table_output(t, "stg_s2_member", "stg_s2_member",
                 [("member_no", "member_no"), ("member_name", "member_name"), ("hp_raw", "hp"), ("phone_norm", "phone_norm"),
                  ("kota_raw", "kota"), ("kota_baku", "kota_final"), ("join_date", "join_d")], 890, 260)
    t.chain("CSV member (S2)", "Normalkan HP dan kota member", "Kota baku member", "Kota member final", "stg_s2_member")
    t.save()


# =====================================================================
# T04  S2 transaksi (42 toko)
# =====================================================================
def t04():
    t = Trans("T04_stg_s2_pos_trx.ktr", "T04_stg_s2_pos_trx",
              "Ekstrak trx_header / trx_line / trx_payment 42 toko (wildcard regex); buang VOID; tanggal DD/MM/YYYY -> date; agregasi SPLIT")
    text_input(t, "CSV trx_header_TSxx (S2)", "${DATA_DIR}/S2_POS_TOKO", "trx_header_TS[0-9]+\\.csv", ";",
               ["trx_no", "store_code", "cashier_id", "member_no", "trx_date", "payment_type", "status"], 80, 80)
    js(t, "Konversi header", """
var trx_date_d = str2date(T(trx_date), "dd/MM/yyyy");
var status_u = T(status) == null ? null : T(status).toUpperCase();
var member_c = T(member_no);
var payment_u = T(payment_type) == null ? null : T(payment_type).toUpperCase();
var waktu_etl = new Date();
""", [("trx_date_d", "Date"), ("status_u", "String"), ("member_c", "String"), ("payment_u", "String"), ("waktu_etl", "Date")], 300, 80)
    filter_rows(t, "Status NORMAL?", "status_u", "NORMAL", "stg_s2_trx_header", "rej_s2_void", 510, 80)
    table_output(t, "stg_s2_trx_header", "stg_s2_trx_header",
                 [("trx_no", "trx_no"), ("store_code", "store_code"), ("cashier_id", "cashier_id"), ("member_no", "member_c"),
                  ("trx_date", "trx_date_d"), ("payment_type", "payment_u"), ("status", "status_u")], 730, 40)
    table_output(t, "rej_s2_void", "rej_s2_void",
                 [("trx_no", "trx_no"), ("store_code", "store_code"), ("trx_date", "trx_date_d"), ("payment_type", "payment_u"),
                  ("status", "status_u"), ("waktu_etl", "waktu_etl")], 730, 140)
    t.chain("CSV trx_header_TSxx (S2)", "Konversi header", "Status NORMAL?")
    t.hop("Status NORMAL?", "stg_s2_trx_header"); t.hop("Status NORMAL?", "rej_s2_void")

    text_input(t, "CSV trx_line_TSxx (S2)", "${DATA_DIR}/S2_POS_TOKO", "trx_line_TS[0-9]+\\.csv", ";",
               ["trx_no", "line_seq", "item_code", "qty", "unit_price_excl", "disc_pct"], 80, 260)
    js(t, "Konversi line", """
var line_seq_i = INT(line_seq); var qty_i = INT(qty);
var harga_n = NUM(unit_price_excl); var disc_n = NUM(disc_pct); if (disc_n == null) disc_n = 0;
""", [("line_seq_i", "Integer"), ("qty_i", "Integer"), ("harga_n", "Number"), ("disc_n", "Number")], 300, 260)
    table_output(t, "stg_s2_trx_line", "stg_s2_trx_line",
                 [("trx_no", "trx_no"), ("line_seq", "line_seq_i"), ("item_code", "item_code"), ("qty", "qty_i"),
                  ("unit_price_excl", "harga_n"), ("disc_pct", "disc_n")], 520, 260)
    t.chain("CSV trx_line_TSxx (S2)", "Konversi line", "stg_s2_trx_line")

    text_input(t, "CSV trx_payment_TSxx (S2)", "${DATA_DIR}/S2_POS_TOKO", "trx_payment_TS[0-9]+\\.csv", ";",
               ["trx_no", "method", "amount"], 80, 400)
    js(t, "Konversi payment", """var amount_n = NUM(amount); if (amount_n == null) amount_n = 0;""", [("amount_n", "Number")], 300, 400)
    sort_rows(t, "Urutkan per trx", [("trx_no", True)], 490, 400)
    group_by(t, "Agregasi pembayaran", ["trx_no"], [("jml_baris_bayar", "method", "COUNT_ALL"), ("total_bayar", "amount_n", "SUM")], 670, 400)
    js(t, "Flag SPLIT", """var is_split = jml_baris_bayar > 1 ? "Y" : "N";""", [("is_split", "String")], 860, 400)
    table_output(t, "stg_s2_trx_payment", "stg_s2_trx_payment",
                 [("trx_no", "trx_no"), ("jml_baris_bayar", "jml_baris_bayar"), ("total_bayar", "total_bayar"), ("is_split", "is_split")], 1050, 400)
    t.chain("CSV trx_payment_TSxx (S2)", "Konversi payment", "Urutkan per trx", "Agregasi pembayaran", "Flag SPLIT", "stg_s2_trx_payment")
    t.save()


# =====================================================================
# T05  S3 marketplace JSON
# =====================================================================
def t05():
    t = Trans("T05_stg_s3_marketplace.ktr", "T05_stg_s3_marketplace",
              "Ekstrak JSON berpaginasi (invoice->items[]->fees), dedup, UTC->WIB, alokasi fee per item")
    json_input(t, "JSON pages (invoice level)", [
        ("invoice", "$.records[*].invoice"), ("paid_at", "$.records[*].paid_at"), ("channel", "$.records[*].channel"),
        ("buyer_hash", "$.records[*].buyer.hash"), ("buyer_city", "$.records[*].buyer.city"),
        ("commission", "$.records[*].fees.commission"), ("service", "$.records[*].fees.service"),
        ("diambil_pada", "$.records[*].diambil_pada"), ("items_json", "$.records[*].items")],
        70, 120, directory="${DATA_DIR}/S3_MPL_API", filemask="mpl_pull_page_[0-9]+\\.json")
    json_input(t, "JSON items[] (explode)", [
        ("seller_sku", "$[*].seller_sku"), ("qty", "$[*].qty"), ("price", "$[*].price"), ("voucher", "$[*].voucher")],
        270, 120, in_field="items_json")
    js(t, "Konversi tipe, UTC->WIB, mapping SKU", """
var paid_utc = str2date(T(paid_at), "yyyy-MM-dd'T'HH:mm:ss'Z'");
var paid_wib = new Date(paid_utc.getTime() + 7 * 3600 * 1000);
var diambil_d = str2date(T(diambil_pada), "yyyy-MM-dd'T'HH:mm:ss");
var qty_i = INT(qty); var price_n = NUM(price); var voucher_n = NUM(voucher); if (voucher_n == null) voucher_n = 0;
var commission_n = NUM(commission); if (commission_n == null) commission_n = 0;
var service_n = NUM(service); if (service_n == null) service_n = 0;
var price_excl = R2(price_n / 1.11); var voucher_excl = R2(voucher_n / 1.11);
var gross_line_incl = qty_i * price_n;
var sku_c = T(seller_sku); var invoice_c = T(invoice);
var material_no = "P-" + sku_c.substring(sku_c.length - 4);
var kota_upper = T(buyer_city) == null ? null : T(buyer_city).toUpperCase().replace(/\\s+/g, " ");
""", [("paid_utc", "Date"), ("paid_wib", "Date"), ("diambil_d", "Date"), ("qty_i", "Integer"), ("price_n", "Number"),
      ("voucher_n", "Number"), ("commission_n", "Number"), ("service_n", "Number"), ("price_excl", "Number"),
      ("voucher_excl", "Number"), ("gross_line_incl", "Number"), ("sku_c", "String"), ("invoice_c", "String"),
      ("material_no", "String"), ("kota_upper", "String")], 480, 120)
    sort_rows(t, "Urut: invoice, sku, tarik terakhir dulu", [("invoice_c", True), ("sku_c", True), ("diambil_d", False)], 700, 120)
    unique_rows(t, "Dedup invoice+seller_sku (ambil terbaru)", ["invoice_c", "sku_c"], 920, 120, distribute="N")
    group_by(t, "Total gross per invoice", ["invoice_c"], [("gross_sum", "gross_line_incl", "SUM")], 1140, 40)
    stream_lookup(t, "Ambil total invoice", "Total gross per invoice", "invoice_c", "invoice_c", [("gross_sum", "gross_sum", "Number")], 1140, 200)
    js(t, "Alokasi fee proporsional", """
var share = gross_sum > 0 ? gross_line_incl / gross_sum : 0;
var fee_komisi_alok = R2(commission_n * share);
var fee_layanan_alok = R2(service_n * share);
""", [("fee_komisi_alok", "Number"), ("fee_layanan_alok", "Number")], 1340, 200)
    db_lookup(t, "Kota baku pembeli", "stg_ref_kota", "kota_upper", "alias_upper", "kota_baku", "kota_lookup", 1540, 200)
    js(t, "Kota pembeli final", """var kota_final = T(kota_lookup) != null ? T(kota_lookup) : T(buyer_city);""", [("kota_final", "String")], 1740, 200)
    table_output(t, "stg_s3_inv_item", "stg_s3_inv_item", [
        ("invoice", "invoice_c"), ("seller_sku", "sku_c"), ("channel", "channel"), ("paid_at_utc", "paid_utc"),
        ("paid_at_wib", "paid_wib"), ("buyer_hash", "buyer_hash"), ("buyer_city", "buyer_city"), ("kota_baku", "kota_final"),
        ("qty", "qty_i"), ("price_incl", "price_n"), ("voucher_incl", "voucher_n"), ("unit_price_excl", "price_excl"),
        ("voucher_excl", "voucher_excl"), ("gross_line_incl", "gross_line_incl"), ("commission_invoice", "commission_n"),
        ("service_invoice", "service_n"), ("fee_komisi_alokasi", "fee_komisi_alok"), ("fee_layanan_alokasi", "fee_layanan_alok"),
        ("material_no", "material_no"), ("diambil_pada", "diambil_d")], 1940, 200)
    t.chain("JSON pages (invoice level)", "JSON items[] (explode)", "Konversi tipe, UTC->WIB, mapping SKU",
            "Urut: invoice, sku, tarik terakhir dulu", "Dedup invoice+seller_sku (ambil terbaru)")
    t.hop("Dedup invoice+seller_sku (ambil terbaru)", "Total gross per invoice")
    t.hop("Dedup invoice+seller_sku (ambil terbaru)", "Ambil total invoice")
    t.hop("Total gross per invoice", "Ambil total invoice")
    t.chain("Ambil total invoice", "Alokasi fee proporsional", "Kota baku pembeli", "Kota pembeli final", "stg_s3_inv_item")
    t.save()


# =====================================================================
# T06  S1 (MySQL OLTP)
# =====================================================================
def t06():
    t = Trans("T06_stg_s1_ecom.ktr", "T06_stg_s1_ecom",
              "Ekstrak S1 dari MySQL nrg_ecom: pelanggan (aturan alamat) dan order line (harga ex-PPN, mapping SKU, voucher, retur)")
    table_input(t, "S1 customers + alamat terpilih", """
SELECT c.customer_id, c.full_name, c.email, c.phone, c.gender, c.birth_date, c.registered_at, a.city, a.province
FROM customers c
LEFT JOIN customer_addresses a
  ON a.address_id = (SELECT x.address_id FROM customer_addresses x
                      WHERE x.customer_id = c.customer_id
                      ORDER BY x.is_primary DESC, x.address_id DESC LIMIT 1)
""", 80, 100, conn="NRG_ECOM")
    js(t, "Normalkan HP dan kota pelanggan", PHONE_JS % ("phone", "phone") + """
var kota_upper = T(city) == null ? null : T(city).toUpperCase().replace(/\\s+/g, " ");
""", [("phone_norm", "String"), ("kota_upper", "String")], 330, 100)
    db_lookup(t, "Kota baku pelanggan", "stg_ref_kota", "kota_upper", "alias_upper", "kota_baku", "kota_lookup", 540, 100)
    js(t, "Kota pelanggan final", """var kota_final = T(kota_lookup) != null ? T(kota_lookup) : T(city);""", [("kota_final", "String")], 750, 100)
    table_output(t, "stg_s1_customer", "stg_s1_customer",
                 [("customer_id", "customer_id"), ("full_name", "full_name"), ("email", "email"), ("phone_raw", "phone"),
                  ("phone_norm", "phone_norm"), ("gender", "gender"), ("birth_date", "birth_date"), ("registered_at", "registered_at"),
                  ("kota_raw", "city"), ("kota_baku", "kota_final"), ("provinsi", "province")], 960, 100)
    t.chain("S1 customers + alamat terpilih", "Normalkan HP dan kota pelanggan", "Kota baku pelanggan", "Kota pelanggan final", "stg_s1_customer")

    table_input(t, "S1 order_items + orders + voucher + retur", """
SELECT i.order_id, i.line_no, o.order_ts, o.status, o.customer_id, o.voucher_id, v.promo_code, v.valid_from AS voucher_valid_from,
       o.payment_method, i.sku, p.product_name, p.brand, c.category_name, pc.category_name AS parent_category,
       i.qty, i.unit_price, i.disc_amount,
       COALESCE(r.qty_retur, 0) AS qty_retur, COALESCE(r.refund, 0) AS refund_incl
FROM order_items i
JOIN orders o               ON o.order_id = i.order_id
LEFT JOIN vouchers v        ON v.voucher_id = o.voucher_id
LEFT JOIN products p        ON p.product_id = i.product_id
LEFT JOIN categories c      ON c.category_id = p.category_id
LEFT JOIN categories pc     ON pc.category_id = c.parent_category_id
LEFT JOIN (SELECT order_item_id, SUM(qty) AS qty_retur, SUM(refund_amount) AS refund
             FROM order_returns WHERE status = 'DISETUJUI' GROUP BY order_item_id) r ON r.order_item_id = i.order_item_id
""", 80, 260, conn="NRG_ECOM")
    js(t, "PPN 11% -> ex-PPN dan mapping SKU", """
var m = /^SKU-([0-9]+)-/.exec("" + sku);
var material_no = m ? ("P-" + m[1]) : ("" + sku);
var unit_excl = R2(unit_price / 1.11);
var disc_excl = R2(disc_amount / 1.11);
var refund_excl = R2(refund_incl / 1.11);
var payment_u = T(payment_method) == null ? null : T(payment_method).toUpperCase();
var promo_u = T(promo_code) == null ? null : T(promo_code).toUpperCase().replace(/\\s+/g, "");
""", [("material_no", "String"), ("unit_excl", "Number"), ("disc_excl", "Number"), ("refund_excl", "Number"),
      ("payment_u", "String"), ("promo_u", "String")], 400, 260)
    table_output(t, "stg_s1_order_line", "stg_s1_order_line", [
        ("order_id", "order_id"), ("line_no", "line_no"), ("order_ts", "order_ts"), ("status", "status"),
        ("customer_id", "customer_id"), ("voucher_id", "voucher_id"), ("promo_code", "promo_u"),
        ("voucher_valid_from", "voucher_valid_from"), ("payment_method", "payment_u"), ("sku", "sku"),
        ("material_no", "material_no"), ("product_name", "product_name"), ("brand", "brand"), ("category_name", "category_name"),
        ("parent_category", "parent_category"), ("qty", "qty"), ("unit_price_incl", "unit_price"),
        ("disc_amount_incl", "disc_amount"), ("unit_price_excl", "unit_excl"), ("disc_excl", "disc_excl"),
        ("qty_retur", "qty_retur"), ("refund_excl", "refund_excl")], 640, 260)
    t.chain("S1 order_items + orders + voucher + retur", "PPN 11% -> ex-PPN dan mapping SKU", "stg_s1_order_line")
    t.save()


# =====================================================================
# T07  Dimensi referensi + map_produk
# =====================================================================
def t07():
    t = Trans("T07_dim_referensi.ktr", "T07_dim_referensi",
              "Muat map_produk, dim_tanggal, dim_toko_kanal, dim_kampanye, dim_metode_bayar")
    table_input(t, "map_produk (S1,S2,S3 -> material_no)", """
SELECT u.sumber, u.kode_sumber, u.material_no, u.aturan,
       CASE WHEN EXISTS (SELECT 1 FROM stg_erp_produk e WHERE e.material_no = u.material_no) THEN 'Y' ELSE 'N' END AS terdaftar_erp
FROM (
  SELECT 'S1' AS sumber, sku AS kode_sumber, MAX(material_no) AS material_no, 'SKU-<nomor>-xxx -> P-<nomor>; selain itu dipakai apa adanya (late arriving)' AS aturan
    FROM stg_s1_order_line GROUP BY sku
  UNION ALL
  SELECT 'S2', item_code, item_code, 'item_code = material_no' FROM (SELECT DISTINCT item_code FROM stg_s2_trx_line) s2
  UNION ALL
  SELECT 'S3', seller_sku, MAX(material_no), 'seller_sku: 4 digit terakhir -> P-<nomor>' FROM stg_s3_inv_item GROUP BY seller_sku
) u
""", 80, 60)
    table_output(t, "map_produk", "map_produk",
                 [("sumber", "sumber"), ("kode_sumber", "kode_sumber"), ("material_no", "material_no"), ("aturan", "aturan"),
                  ("terdaftar_erp", "terdaftar_erp")], 480, 60)
    t.chain("map_produk (S1,S2,S3 -> material_no)", "map_produk")

    table_input(t, "Bangun dim_tanggal (2022-2023)", """
WITH RECURSIVE d(tgl) AS (
  SELECT DATE('2022-01-01') UNION ALL SELECT DATE_ADD(tgl, INTERVAL 1 DAY) FROM d WHERE tgl < DATE('2023-12-31')
)
SELECT CAST(DATE_FORMAT(tgl, '%Y%m%d') AS UNSIGNED) AS tanggal_key, tgl AS tanggal, DAY(tgl) AS hari,
       ELT(WEEKDAY(tgl) + 1, 'Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu') AS nama_hari,
       WEEK(tgl, 3) AS minggu_ke, MONTH(tgl) AS bulan,
       ELT(MONTH(tgl), 'Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember') AS nama_bulan,
       QUARTER(tgl) AS kuartal, YEAR(tgl) AS tahun, CONCAT(YEAR(tgl), '-Q', QUARTER(tgl)) AS tahun_kuartal,
       CASE WHEN WEEKDAY(tgl) >= 5 THEN 'Y' ELSE 'N' END AS is_weekend
FROM d
""", 80, 180)
    table_output(t, "dim_tanggal", "dim_tanggal",
                 [(c, c) for c in ["tanggal_key", "tanggal", "hari", "nama_hari", "minggu_ke", "bulan", "nama_bulan", "kuartal",
                                   "tahun", "tahun_kuartal", "is_weekend"]], 480, 180)
    t.chain("Bangun dim_tanggal (2022-2023)", "dim_tanggal")

    table_input(t, "Toko dan kanal (S2 store_master + WEB + MPL)", """
SELECT store_code AS kode_toko_kanal, store_name AS nama_toko_kanal, 'Toko Fisik' AS kanal, 'POS Toko' AS platform,
       kota_baku, province AS provinsi, format_toko, 'S2_POS' AS sistem_sumber
  FROM stg_s2_store
UNION ALL SELECT 'WEB',   'Situs Web NRG',  'Situs Web',   'Website NRG',   NULL, NULL, NULL, 'S1_WEB'
UNION ALL SELECT 'MPL_A', 'Marketplace A',  'Marketplace', 'marketplace_a', NULL, NULL, NULL, 'S3_MPL'
UNION ALL SELECT 'MPL_B', 'Marketplace B',  'Marketplace', 'marketplace_b', NULL, NULL, NULL, 'S3_MPL'
""", 80, 300)
    table_output(t, "dim_toko_kanal", "dim_toko_kanal",
                 [(c, c) for c in ["kode_toko_kanal", "nama_toko_kanal", "kanal", "platform", "kota_baku", "provinsi", "format_toko", "sistem_sumber"]], 480, 300)
    t.chain("Toko dan kanal (S2 store_master + WEB + MPL)", "dim_toko_kanal")

    table_input(t, "Kampanye valid (S5)", """
SELECT kode_promo, nama_kampanye, jenis_promo, kanal AS kanal_target, tgl_mulai, tgl_selesai, target_diskon_persen, pic,
       'VALID' AS status_validasi
FROM stg_s5_kampanye
""", 80, 420)
    table_output(t, "dim_kampanye", "dim_kampanye",
                 [(c, c) for c in ["kode_promo", "nama_kampanye", "jenis_promo", "kanal_target", "tgl_mulai", "tgl_selesai",
                                   "target_diskon_persen", "pic", "status_validasi"]], 480, 420)
    t.chain("Kampanye valid (S5)", "dim_kampanye")

    table_input(t, "Metode bayar (S1 + S2 + SPLIT)", """
SELECT m.metode_bayar,
       CASE WHEN m.metode_bayar IN ('CASH','TUNAI') THEN 'Tunai'
            WHEN m.metode_bayar = 'SPLIT' THEN 'Campuran'
            ELSE 'Non-tunai' END AS kelompok_bayar
FROM (
  SELECT DISTINCT payment_method AS metode_bayar FROM stg_s1_order_line WHERE payment_method IS NOT NULL
  UNION SELECT DISTINCT payment_type FROM stg_s2_trx_header WHERE payment_type IS NOT NULL
  UNION SELECT 'SPLIT'
) m
""", 80, 540)
    table_output(t, "dim_metode_bayar", "dim_metode_bayar", [("metode_bayar", "metode_bayar"), ("kelompok_bayar", "kelompok_bayar")], 480, 540)
    t.chain("Metode bayar (S1 + S2 + SPLIT)", "dim_metode_bayar")
    t.save()


# =====================================================================
# T08 dim_pemasok ; T09 dim_produk ; T10 dim_pelanggan
# =====================================================================
def t08():
    t = Trans("T08_dim_pemasok.ktr", "T08_dim_pemasok", "Muat dim_pemasok dari stg_erp_pemasok")
    table_input(t, "stg_erp_pemasok", "SELECT supplier_id, nama_supplier, kota, kontak FROM stg_erp_pemasok ORDER BY supplier_id", 80, 80)
    table_output(t, "dim_pemasok", "dim_pemasok", [(c, c) for c in ["supplier_id", "nama_supplier", "kota", "kontak"]], 360, 80)
    t.chain("stg_erp_pemasok", "dim_pemasok")
    t.save()


def t09():
    t = Trans("T09_dim_produk.ktr", "T09_dim_produk",
              "Muat dim_produk (SCD Tipe 2 pada harga pokok ERP) + baris inferred untuk late arriving dimension")
    table_input(t, "Versi produk ERP + produk late arriving", """
SELECT e.material_no, e.nama_produk, e.brand, e.kategori, e.sub_kategori, ps.pemasok_key, e.supplier AS nama_pemasok,
       e.status AS status_erp, e.harga_pokok, e.berlaku_sejak,
       CASE WHEN e.berlaku_sejak = (SELECT MIN(x.berlaku_sejak) FROM stg_erp_produk x WHERE x.material_no = e.material_no)
            THEN DATE('1900-01-01') ELSE e.berlaku_sejak END AS tgl_efektif_awal,
       COALESCE(DATE_SUB((SELECT MIN(y.berlaku_sejak) FROM stg_erp_produk y
                           WHERE y.material_no = e.material_no AND y.berlaku_sejak > e.berlaku_sejak), INTERVAL 1 DAY),
                DATE('9999-12-31')) AS tgl_efektif_akhir,
       CASE WHEN EXISTS (SELECT 1 FROM stg_erp_produk z WHERE z.material_no = e.material_no AND z.berlaku_sejak > e.berlaku_sejak)
            THEN 'N' ELSE 'Y' END AS is_current,
       'N' AS is_inferred
FROM stg_erp_produk e
LEFT JOIN (SELECT nama_supplier, MIN(pemasok_key) AS pemasok_key FROM dim_pemasok GROUP BY nama_supplier) ps
       ON ps.nama_supplier = e.supplier
UNION ALL
SELECT m.material_no, COALESCE(MAX(s.product_name), m.material_no), MAX(s.brand),
       COALESCE(MAX(s.parent_category), 'Tidak diketahui'), COALESCE(MAX(s.category_name), 'Tidak diketahui'),
       NULL, NULL, 'INFERRED', NULL, CAST(NULL AS DATE), DATE('1900-01-01'), DATE('9999-12-31'), 'Y', 'Y'
FROM map_produk m
LEFT JOIN (SELECT sku, MAX(product_name) AS product_name, MAX(brand) AS brand,
                  MAX(parent_category) AS parent_category, MAX(category_name) AS category_name
             FROM stg_s1_order_line GROUP BY sku) s ON m.sumber = 'S1' AND s.sku = m.kode_sumber
WHERE m.terdaftar_erp = 'N'
GROUP BY m.material_no
""", 80, 80)
    table_output(t, "dim_produk", "dim_produk",
                 [(c, c) for c in ["material_no", "nama_produk", "brand", "kategori", "sub_kategori", "pemasok_key", "nama_pemasok",
                                   "status_erp", "harga_pokok", "berlaku_sejak", "tgl_efektif_awal", "tgl_efektif_akhir",
                                   "is_current", "is_inferred"]], 400, 80)
    t.chain("Versi produk ERP + produk late arriving", "dim_produk")
    t.save()


def t10():
    t = Trans("T10_dim_pelanggan.ktr", "T10_dim_pelanggan",
              "Muat dim_pelanggan terpadu: pelanggan web dipadankan ke member toko via nomor HP ternormalisasi; pembeli marketplace per buyer.hash")
    table_input(t, "Gabung web + member + marketplace", """
SELECT CASE WHEN m.member_no IS NULL THEN 'WEB_ONLY' ELSE 'OMNICHANNEL' END AS tipe_pelanggan,
       w.customer_id AS customer_id_web, m.member_no, CAST(NULL AS CHAR(20)) AS mpl_buyer_hash, w.phone_norm,
       w.full_name AS nama_pelanggan, w.gender, COALESCE(w.kota_baku, m.kota_baku) AS kota_baku, w.provinsi,
       w.registered_at AS tgl_daftar_web, m.join_date AS tgl_join_member,
       'Y' AS is_web_customer, CASE WHEN m.member_no IS NULL THEN 'N' ELSE 'Y' END AS is_member_toko
FROM stg_s1_customer w
LEFT JOIN stg_s2_member m ON m.phone_norm = w.phone_norm
UNION ALL
SELECT 'MEMBER_TOKO', CAST(NULL AS SIGNED), m.member_no, NULL, m.phone_norm, m.member_name, CAST(NULL AS CHAR(1)), m.kota_baku,
       CAST(NULL AS CHAR(60)), CAST(NULL AS DATETIME), m.join_date, 'N', 'Y'
FROM stg_s2_member m
WHERE NOT EXISTS (SELECT 1 FROM stg_s1_customer w WHERE w.phone_norm = m.phone_norm)
UNION ALL
SELECT 'MARKETPLACE', CAST(NULL AS SIGNED), NULL, b.buyer_hash, NULL, CONCAT('Pembeli marketplace ', b.buyer_hash), CAST(NULL AS CHAR(1)),
       b.kota_baku, CAST(NULL AS CHAR(60)), CAST(NULL AS DATETIME), CAST(NULL AS DATE), 'N', 'N'
FROM (SELECT buyer_hash, MAX(kota_baku) AS kota_baku FROM stg_s3_inv_item GROUP BY buyer_hash) b
""", 80, 80)
    table_output(t, "dim_pelanggan", "dim_pelanggan",
                 [(c, c) for c in ["tipe_pelanggan", "customer_id_web", "member_no", "mpl_buyer_hash", "phone_norm", "nama_pelanggan",
                                   "gender", "kota_baku", "provinsi", "tgl_daftar_web", "tgl_join_member", "is_web_customer", "is_member_toko"]], 400, 80)
    t.chain("Gabung web + member + marketplace", "dim_pelanggan")
    t.save()


# =====================================================================
# T11 fact
# =====================================================================
CAMPAIGN_WINDOW = """
COALESCE((SELECT k.kampanye_key FROM dim_kampanye k
           WHERE k.kampanye_key > 0 AND {dt} BETWEEN k.tgl_mulai AND k.tgl_selesai
             AND k.kanal_target IN ('Semua Kanal', {kanal})
           ORDER BY (k.kanal_target = 'Semua Kanal'), k.tgl_mulai DESC LIMIT 1), -1)"""

FACT_COLS = ["sumber_sistem", "no_transaksi", "no_baris", "tanggal_key", "waktu_wib", "produk_key", "pelanggan_key", "toko_kanal_key",
             "kampanye_key", "metode_bayar_key", "qty", "harga_satuan", "diskon_excl", "hpp_satuan", "fee_komisi", "fee_layanan",
             "qty_retur", "nilai_retur"]


def t11():
    t = Trans("T11_fact_penjualan.ktr", "T11_fact_penjualan",
              "Muat fact_penjualan dari tiga kanal (S1, S2, S3): lookup surrogate key, hitung penjualan bersih, HPP (SCD2 per tanggal transaksi) dan margin kotor")
    s1 = """SELECT 'S1_WEB' AS sumber_sistem, l.order_id AS no_transaksi, CAST(l.line_no AS SIGNED) AS no_baris,
       CAST(DATE_FORMAT(l.order_ts, '%Y%m%d') AS UNSIGNED) AS tanggal_key, l.order_ts AS waktu_wib,
       p.produk_key, COALESCE(pl.pelanggan_key, -1) AS pelanggan_key, tk.toko_kanal_key,
       CAST(CASE WHEN l.voucher_id IS NOT NULL AND l.disc_amount_incl > 0 THEN COALESCE(k.kampanye_key, -2) ELSE -1 END AS SIGNED) AS kampanye_key,
       CAST(COALESCE(mb.metode_bayar_key, -1) AS SIGNED) AS metode_bayar_key,
       CAST(l.qty AS SIGNED) AS qty, l.unit_price_excl AS harga_satuan, l.disc_excl AS diskon_excl, p.harga_pokok AS hpp_satuan,
       CAST(0 AS DECIMAL(18,2)) AS fee_komisi, CAST(0 AS DECIMAL(18,2)) AS fee_layanan, CAST(l.qty_retur AS SIGNED) AS qty_retur, CAST(l.refund_excl AS DECIMAL(18,2)) AS nilai_retur
FROM stg_s1_order_line l
JOIN map_produk mp ON mp.sumber = 'S1' AND mp.kode_sumber = l.sku
JOIN dim_produk p  ON p.material_no = mp.material_no AND DATE(l.order_ts) BETWEEN p.tgl_efektif_awal AND p.tgl_efektif_akhir
JOIN dim_toko_kanal tk ON tk.kode_toko_kanal = 'WEB'
LEFT JOIN dim_pelanggan pl ON pl.customer_id_web = l.customer_id
LEFT JOIN dim_kampanye k ON k.kode_promo = l.promo_code AND k.tgl_mulai = l.voucher_valid_from
LEFT JOIN dim_metode_bayar mb ON mb.metode_bayar = l.payment_method
WHERE l.status <> 'DIBATALKAN'"""

    s2 = """SELECT 'S2_POS' AS sumber_sistem, l.trx_no AS no_transaksi, CAST(l.line_seq AS SIGNED) AS no_baris,
       CAST(DATE_FORMAT(h.trx_date, '%Y%m%d') AS UNSIGNED) AS tanggal_key, CAST(h.trx_date AS DATETIME) AS waktu_wib,
       p.produk_key, COALESCE(pl.pelanggan_key, -1) AS pelanggan_key, tk.toko_kanal_key,
       CAST(CASE WHEN l.disc_pct > 0 THEN """ + CAMPAIGN_WINDOW.format(dt="h.trx_date", kanal="'Toko Fisik'") + """ ELSE -1 END AS SIGNED) AS kampanye_key,
       CAST(COALESCE(mb.metode_bayar_key, -1) AS SIGNED) AS metode_bayar_key,
       CAST(l.qty AS SIGNED) AS qty, l.unit_price_excl AS harga_satuan, ROUND(l.qty * l.unit_price_excl * l.disc_pct / 100, 2) AS diskon_excl,
       p.harga_pokok AS hpp_satuan, CAST(0 AS DECIMAL(18,2)) AS fee_komisi, CAST(0 AS DECIMAL(18,2)) AS fee_layanan, CAST(0 AS SIGNED) AS qty_retur, CAST(0 AS DECIMAL(18,2)) AS nilai_retur
FROM stg_s2_trx_line l
JOIN stg_s2_trx_header h ON h.trx_no = l.trx_no
LEFT JOIN stg_s2_trx_payment pay ON pay.trx_no = l.trx_no
JOIN map_produk mp ON mp.sumber = 'S2' AND mp.kode_sumber = l.item_code
JOIN dim_produk p  ON p.material_no = mp.material_no AND h.trx_date BETWEEN p.tgl_efektif_awal AND p.tgl_efektif_akhir
JOIN dim_toko_kanal tk ON tk.kode_toko_kanal = h.store_code
LEFT JOIN dim_pelanggan pl ON pl.member_no = h.member_no
LEFT JOIN dim_metode_bayar mb ON mb.metode_bayar = CASE WHEN h.payment_type = 'SPLIT' OR COALESCE(pay.jml_baris_bayar, 1) > 1 THEN 'SPLIT' ELSE h.payment_type END"""

    s3 = """SELECT 'S3_MPL' AS sumber_sistem, s.invoice AS no_transaksi,
       CAST(ROW_NUMBER() OVER (PARTITION BY s.invoice ORDER BY s.seller_sku) AS SIGNED) AS no_baris,
       CAST(DATE_FORMAT(s.paid_at_wib, '%Y%m%d') AS UNSIGNED) AS tanggal_key, s.paid_at_wib AS waktu_wib,
       p.produk_key, COALESCE(pl.pelanggan_key, -1) AS pelanggan_key, tk.toko_kanal_key,
       CAST(CASE WHEN s.voucher_excl > 0 THEN """ + CAMPAIGN_WINDOW.format(dt="DATE(s.paid_at_wib)", kanal="'Marketplace'") + """ ELSE -1 END AS SIGNED) AS kampanye_key,
       CAST(-1 AS SIGNED) AS metode_bayar_key,
       CAST(s.qty AS SIGNED) AS qty, s.unit_price_excl AS harga_satuan, s.voucher_excl AS diskon_excl, p.harga_pokok AS hpp_satuan,
       s.fee_komisi_alokasi AS fee_komisi, s.fee_layanan_alokasi AS fee_layanan, CAST(0 AS SIGNED) AS qty_retur, CAST(0 AS DECIMAL(18,2)) AS nilai_retur
FROM stg_s3_inv_item s
JOIN map_produk mp ON mp.sumber = 'S3' AND mp.kode_sumber = s.seller_sku
JOIN dim_produk p  ON p.material_no = mp.material_no AND DATE(s.paid_at_wib) BETWEEN p.tgl_efektif_awal AND p.tgl_efektif_akhir
JOIN dim_toko_kanal tk ON tk.kode_toko_kanal = CASE s.channel WHEN 'marketplace_a' THEN 'MPL_A' ELSE 'MPL_B' END
LEFT JOIN dim_pelanggan pl ON pl.mpl_buyer_hash = s.buyer_hash"""

    sql_union = f"{s1}\nUNION ALL\n{s2}\nUNION ALL\n{s3}"
    table_input(t, "Ekstrak transaksi (S1, S2, S3)", sql_union, 120, 180)
    js(t, "Hitung bersih, HPP, margin kotor", """
var penjualan_kotor = R2(qty * harga_satuan);
var penjualan_bersih = R2(penjualan_kotor - diskon_excl);
var hpp_total = (hpp_satuan == null) ? null : R2(qty * hpp_satuan);
var margin_kotor = (hpp_total == null) ? null : R2(penjualan_bersih - hpp_total - fee_komisi - fee_layanan);
""", [("penjualan_kotor", "Number"), ("penjualan_bersih", "Number"), ("hpp_total", "Number"), ("margin_kotor", "Number")], 460, 180)
    table_output(t, "fact_penjualan", "fact_penjualan", [
        ("sumber_sistem", "sumber_sistem"), ("no_transaksi", "no_transaksi"), ("no_baris", "no_baris"), ("tanggal_key", "tanggal_key"),
        ("waktu_transaksi_wib", "waktu_wib"), ("produk_key", "produk_key"), ("pelanggan_key", "pelanggan_key"),
        ("toko_kanal_key", "toko_kanal_key"), ("kampanye_key", "kampanye_key"), ("metode_bayar_key", "metode_bayar_key"),
        ("qty", "qty"), ("harga_satuan_excl_ppn", "harga_satuan"), ("penjualan_kotor_excl", "penjualan_kotor"),
        ("diskon_excl_ppn", "diskon_excl"), ("penjualan_bersih_excl", "penjualan_bersih"), ("harga_pokok_satuan", "hpp_satuan"),
        ("harga_pokok_total", "hpp_total"), ("fee_komisi", "fee_komisi"), ("fee_layanan", "fee_layanan"),
        ("margin_kotor", "margin_kotor"), ("qty_retur", "qty_retur"), ("nilai_retur_excl_ppn", "nilai_retur")], 780, 180)
    t.chain("Ekstrak transaksi (S1, S2, S3)", "Hitung bersih, HPP, margin kotor", "fact_penjualan")
    t.save()


# =====================================================================
# JOB
# =====================================================================
def job():
    seq = [
        ("T01 Staging S4 ERP + ref_kota", "T01_stg_s4_erp_ref_kota.ktr"),
        ("T02 Staging S5 Kampanye", "T02_stg_s5_kampanye.ktr"),
        ("T03 Staging S2 Master (toko, member)", "T03_stg_s2_master.ktr"),
        ("T04 Staging S2 Transaksi POS", "T04_stg_s2_pos_trx.ktr"),
        ("T05 Staging S3 Marketplace", "T05_stg_s3_marketplace.ktr"),
        ("T06 Staging S1 Ecom", "T06_stg_s1_ecom.ktr"),
        ("T07 Dimensi referensi", "T07_dim_referensi.ktr"),
        ("T08 dim_pemasok", "T08_dim_pemasok.ktr"),
        ("T09 dim_produk", "T09_dim_produk.ktr"),
        ("T10 dim_pelanggan", "T10_dim_pelanggan.ktr"),
        ("T11 fact_penjualan", "T11_fact_penjualan.ktr"),
    ]
    entries = [
        """<entry><name>START</name><description/><type>SPECIAL</type><start>Y</start><dummy>N</dummy><repeat>N</repeat>
<schedulerType>0</schedulerType><intervalSeconds>0</intervalSeconds><intervalMinutes>60</intervalMinutes><hour>12</hour>
<minutes>0</minutes><weekDay>1</weekDay><DayOfMonth>1</DayOfMonth><parallel>N</parallel><draw>Y</draw><nr>0</nr><xloc>40</xloc><yloc>60</yloc></entry>""",
        """<entry><name>Reset DW (hapus staging, dimensi, fakta)</name><description/><type>SQL</type><sql/>
<useVariableSubstitution>F</useVariableSubstitution><sqlfromfile>T</sqlfromfile>
<sqlfilename>${Internal.Entry.Current.Directory}/../sql/02_reset_dw.sql</sqlfilename><sendOneStatement>F</sendOneStatement>
<connection>NRG_DW</connection><parallel>N</parallel><draw>Y</draw><nr>0</nr><xloc>200</xloc><yloc>60</yloc></entry>"""]
    hops, prev, x = [], "START", 200
    hops.append(("START", "Reset DW (hapus staging, dimensi, fakta)"))
    prev = "Reset DW (hapus staging, dimensi, fakta)"
    for i, (nm, fn) in enumerate(seq):
        x = 380 + i * 170
        entries.append(f"""<entry><name>{nm}</name><description/><type>TRANS</type><specification_method>filename</specification_method>
<filename>${{Internal.Entry.Current.Directory}}/{fn}</filename><transname/><arg_from_previous>N</arg_from_previous>
<params_from_previous>N</params_from_previous><exec_per_row>N</exec_per_row><clear_rows>N</clear_rows><clear_files>N</clear_files>
<set_logfile>N</set_logfile><logfile/><logext/><add_date>N</add_date><add_time>N</add_time><loglevel>Basic</loglevel>
<cluster>N</cluster><slave_server_name/><set_append_logfile>N</set_append_logfile><wait_until_finished>Y</wait_until_finished>
<follow_abort_remote>N</follow_abort_remote><create_parent_folder>N</create_parent_folder><logging_remote_work>N</logging_remote_work>
<run_configuration>Pentaho local</run_configuration><parameters><pass_all_parameters>Y</pass_all_parameters></parameters>
<parallel>N</parallel><draw>Y</draw><nr>0</nr><xloc>{x}</xloc><yloc>{60 + (i % 2) * 70}</yloc></entry>""")
        hops.append((prev, nm)); prev = nm
    hop_xml = "".join(f"<hop><from>{a}</from><to>{b}</to><from_nr>0</from_nr><to_nr>0</to_nr><enabled>Y</enabled><evaluation>Y</evaluation><unconditional>{'Y' if a == 'START' else 'N'}</unconditional></hop>" for a, b in hops)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<job><name>J_NRG_DW_Main</name><description>Orkestrasi ETL NRG Data Warehouse (S1-S5 -> star schema)</description><extended_description/>
<job_version/><job_status>0</job_status><directory>/</directory><created_user>kelompok4</created_user><created_date>2026/10/13 12:00:00.000</created_date>
<modified_user>kelompok4</modified_user><modified_date>2026/10/13 12:00:00.000</modified_date>
{params_xml()}
{conn_xml("NRG_DW", "DW_DB")}
{conn_xml("NRG_ECOM", "ECOM_DB")}
<slaveservers/>
<job-log-table><connection/><schema/><table/><size_limit_lines/><interval/><timeout_days/></job-log-table>
<jobentry-log-table><connection/><schema/><table/><timeout_days/></jobentry-log-table>
<channel-log-table><connection/><schema/><table/><timeout_days/></channel-log-table>
<checkpoint-log-table><connection/><schema/><table/><timeout_days/></checkpoint-log-table>
<entries>{"".join(entries)}</entries>
<hops>{hop_xml}</hops>
<notepads/>
</job>
"""
    with open(os.path.join(OUT, "J_NRG_DW_Main.kjb"), "w", encoding="utf-8") as f:
        f.write(xml)
    print("ditulis J_NRG_DW_Main.kjb")


if __name__ == "__main__":
    for fn in (t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, job):
        fn()







