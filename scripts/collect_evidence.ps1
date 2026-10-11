# scripts/collect_evidence.ps1
# Extracts real execution evidence directly from the Hadoop cluster into evidence/

$ErrorActionPreference = "Stop"

$evidenceDir = Join-Path $PSScriptRoot "..\evidence"
if (-not (Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
}

Write-Host "--> Extracting HDFS Cluster Report..." -ForegroundColor Yellow
docker exec namenode hdfs dfsadmin -report | Out-File -FilePath (Join-Path $evidenceDir "hdfs_status.txt") -Encoding utf8

Write-Host "--> Extracting HDFS Data Listing..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -ls -h /data/olist | Out-File -FilePath (Join-Path $evidenceDir "hdfs_data_listing.txt") -Encoding utf8

Write-Host "--> Extracting Job 01 Output..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /output/job01_order_statistics/part-00000 | Out-File -FilePath (Join-Path $evidenceDir "job01_output.txt") -Encoding utf8

Write-Host "--> Extracting Job 02 Output (sample)..." -ForegroundColor Yellow
docker exec namenode bash -c "hdfs dfs -cat /output/job02_revenue/part-00000 2>/dev/null | head -n 100" | Out-File -FilePath (Join-Path $evidenceDir "job02_output.txt") -Encoding utf8
docker exec namenode bash -c "hdfs dfs -cat /output/job02_monthly_revenue/part-00000 2>/dev/null" | Out-File -FilePath (Join-Path $evidenceDir "job02_monthly_revenue_output.txt") -Encoding utf8


Write-Host "--> Extracting Job 03 Output..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /output/job03_category/part-00000 | Out-File -FilePath (Join-Path $evidenceDir "job03_output.txt") -Encoding utf8

Write-Host "--> Extracting Job 04 Output (sample)..." -ForegroundColor Yellow
docker exec namenode bash -c "hdfs dfs -cat /output/job04_seller/part-00000 2>/dev/null | head -n 100" | Out-File -FilePath (Join-Path $evidenceDir "job04_output.txt") -Encoding utf8


Write-Host "--> Extracting Job 05 Output..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /output/job05_reviews/part-00000 | Out-File -FilePath (Join-Path $evidenceDir "job05_reviews_output.txt") -Encoding utf8

Write-Host "--> Extracting Job 06 Output..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /output/job06_delivery/part-00000 | Out-File -FilePath (Join-Path $evidenceDir "job06_delivery_output.txt") -Encoding utf8

Write-Host "`n[SUCCESS] All evidence files generated in evidence/ folder!" -ForegroundColor Green
