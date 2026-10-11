# scripts/init_hdfs.ps1
# Prepares HDFS folders and uploads raw datasets if not already uploaded.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " [HDFS] Initializing Hadoop HDFS Storage Layer   " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if namenode container is running
$nnState = docker inspect -f '{{.State.Running}}' namenode 2>$null
if ($nnState -ne "true") {
    Write-Error "NameNode container is not running! Please start containers first using scripts/start.ps1"
    exit 1
}

Write-Host "--> Checking NameNode connectivity..." -ForegroundColor Yellow
docker exec namenode hdfs dfsadmin -safemode get
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to connect to HDFS NameNode!"
    exit 1
}

Write-Host "--> Creating HDFS directory structure: /data/olist/raw, /data/olist/processed, /data/olist/output..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -mkdir -p /data/olist/raw
docker exec namenode hdfs dfs -mkdir -p /data/olist/processed
docker exec namenode hdfs dfs -mkdir -p /data/olist/output

# Check if datasets exist in /data/olist
Write-Host "--> Checking existing datasets on HDFS..." -ForegroundColor Yellow
$hdfsFiles = docker exec namenode hdfs dfs -ls /data/olist 2>$null

$expectedCsvs = @(
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
)

$localDataDir = Join-Path $PSScriptRoot "..\data"

foreach ($csv in $expectedCsvs) {
    $existsOnHdfs = $hdfsFiles -match $csv
    if (-not $existsOnHdfs) {
        $localPath = Join-Path $localDataDir $csv
        if (Test-Path $localPath) {
            Write-Host "--> Uploading $csv to /data/olist/..." -ForegroundColor Green
            # Copy to namenode temp then put to HDFS to handle Windows paths safely
            docker cp $localPath namenode:/tmp/$csv
            docker exec namenode hdfs dfs -put -f /tmp/$csv /data/olist/$csv
            docker exec namenode rm -f /tmp/$csv
        } else {
            Write-Warning "Local file $localPath not found. Skipping upload."
        }
    } else {
        Write-Host "  [OK] $csv is already on HDFS." -ForegroundColor Gray
    }
}

Write-Host "`n================ HDFS DIRECTORY LISTING ================" -ForegroundColor Cyan
docker exec namenode hdfs dfs -ls /data/olist
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to list HDFS directory!"
    exit 1
}

Write-Host "`n================ HDFS DISK USAGE (-du -h) ================" -ForegroundColor Cyan
docker exec namenode hdfs dfs -du -h /data/olist

Write-Host "`n================ HDFS CLUSTER HEALTH REPORT ================" -ForegroundColor Cyan
docker exec namenode hdfs dfsadmin -report | Select-Object -First 18

Write-Host "`n[SUCCESS] HDFS initialization completed successfully!" -ForegroundColor Green
