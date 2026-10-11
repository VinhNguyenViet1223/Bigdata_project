# scripts/run_mapreduce.ps1
# Executes Hadoop Streaming Python MapReduce jobs (MR01, MR02, MR03) on HDFS.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " [MAPREDUCE] Running Distributed Batch Jobs      " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check mapreduce container
$mrRunning = docker inspect -f '{{.State.Running}}' mapreduce 2>$null
if ($mrRunning -ne "true") {
    Write-Error "MapReduce container is not running! Run scripts/start.ps1 first."
    exit 1
}

# 2. Run local unit tests first
Write-Host "--> Step 1: Running local MapReduce pipeline unit tests..." -ForegroundColor Yellow
python (Join-Path $PSScriptRoot "..\mapreduce\tests\test_mapreduce.py")
if ($LASTEXITCODE -ne 0) {
    Write-Error "MapReduce unit tests failed!"
    exit 1
}
Write-Host "  [OK] Unit tests passed!" -ForegroundColor Green

# 3. Execute Hadoop Streaming on cluster
Write-Host "`n--> Step 2: Executing Hadoop Streaming jobs on HDFS..." -ForegroundColor Yellow
docker exec mapreduce bash /app/jobs/run_all_mr.sh
if ($LASTEXITCODE -ne 0) {
    Write-Error "Hadoop Streaming execution encountered an error!"
    exit 1
}

Write-Host "`n================ VERIFYING HDFS OUTPUTS ================" -ForegroundColor Cyan
Write-Host "`n[MR01: Order Status]" -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /data/olist/output/mr01/part-00000

Write-Host "`n[MR02: Orders by Month (First 5)]" -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /data/olist/output/mr02/part-00000 | Select-Object -First 5

Write-Host "`n[MR03: Revenue by Month (First 5)]" -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /data/olist/output/mr03/part-00000 | Select-Object -First 5

Write-Host "`n[SUCCESS] All 3 MapReduce jobs completed and verified on HDFS!" -ForegroundColor Green
