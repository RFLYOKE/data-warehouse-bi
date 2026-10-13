# Menjalankan pipeline NRG DW dari kondisi kosong.
# Pemakaian:  powershell -ExecutionPolicy Bypass -File NRG_DW\run_pipeline.ps1
# Ubah variabel di bagian KONFIGURASI sesuai mesin Anda.

# ---------------- KONFIGURASI ----------------
$PDI_HOME   = "C:\pdi\data-integration"                               # folder Pentaho Data Integration
$JAVA_HOME  = "C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot"       # PDI 10.x butuh Java 11/17
$MYSQL_EXE  = "C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysql.exe"
$DB_HOST = "localhost"; $DB_PORT = "3306"; $DB_USER = "root"; $DB_PASS = ""
$LOAD_S1    = $true      # true = (re)load S1 ke MySQL nrg_ecom via load_all.py
# ---------------------------------------------
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$DATA = (Resolve-Path (Join-Path $ROOT "..\Data")).Path -replace '\\','/'
$mysqlPass = if ($DB_PASS -ne "") { "-p$DB_PASS" } else { "" }

Write-Host "== 1. Buat database nrg_dw (DDL)"
Get-Content (Join-Path $ROOT "sql\01_ddl_dw.sql") -Raw | & $MYSQL_EXE -h $DB_HOST -P $DB_PORT -u $DB_USER $mysqlPass

if ($LOAD_S1) {
    Write-Host "== 2. Muat S1 ke MySQL (schema nrg_ecom + load_all.py)"
    & $MYSQL_EXE -h $DB_HOST -P $DB_PORT -u $DB_USER $mysqlPass -e "DROP DATABASE IF EXISTS nrg_ecom;"
    Get-Content (Join-Path $ROOT "..\Data\S1_ecom_db_schema_mysql.sql") -Raw | & $MYSQL_EXE -h $DB_HOST -P $DB_PORT -u $DB_USER $mysqlPass
    Push-Location (Join-Path $ROOT "..\Data"); python load_all.py; Pop-Location
}

Write-Host "== 3. Jalankan Job Pentaho J_NRG_DW_Main"
$env:JAVA_HOME = $JAVA_HOME; $env:PENTAHO_JAVA_HOME = $JAVA_HOME; $env:PATH = "$JAVA_HOME\bin;$env:PATH"
$env:KETTLE_HOME = Join-Path $ROOT "kettle_home"; New-Item -ItemType Directory -Force $env:KETTLE_HOME | Out-Null
& "$PDI_HOME\Kitchen.bat" "/file:$ROOT\pentaho\J_NRG_DW_Main.kjb" "/level:Basic" `
    "-param:DATA_DIR=$DATA" "-param:DB_HOST=$DB_HOST" "-param:DB_PORT=$DB_PORT" "-param:DB_USER=$DB_USER" "-param:DB_PASS=$DB_PASS" |
    Tee-Object -FilePath (Join-Path $ROOT "etl_run.log")
Write-Host "== Selesai. Validasi: mysql < sql\03_validasi_etl.sql ; Kueri pembuktian: sql\04_kueri_pembuktian.sql"
