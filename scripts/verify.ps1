# scripts/verify.ps1
# End-to-end verification script for all Big Data layers.

$ErrorActionPreference = "Continue"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " [VERIFICATION] End-to-End System Audit          " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$passedChecks = 0
$totalChecks = 7

# 1. Docker Containers
Write-Host "`n[1/$totalChecks] Checking Docker Containers..." -ForegroundColor Yellow
$containers = @("namenode", "datanode", "spark-master", "spark-worker", "mongodb", "elasticsearch", "mapreduce")
$allRunning = $true
foreach ($c in $containers) {
    $st = docker inspect -f '{{.State.Running}}' $c 2>$null
    if ($st -ne "true") {
        Write-Host "  FAIL: Container $c is NOT running" -ForegroundColor Red
        $allRunning = $false
    }
}
if ($allRunning) {
    Write-Host "  PASS: All 7 core Docker containers are active" -ForegroundColor Green
    $passedChecks++
}

# 2. HDFS Raw Dataset
Write-Host "`n[2/$totalChecks] Checking HDFS Storage Layer..." -ForegroundColor Yellow
$rawCount = (docker exec namenode hdfs dfs -ls /data/olist 2>$null | Select-String "\.csv").Count
if ($rawCount -ge 9) {
    Write-Host "  PASS: HDFS contains $rawCount raw Olist CSV datasets" -ForegroundColor Green
    $passedChecks++
} else {
    Write-Host "  FAIL: Found only $rawCount CSV files on HDFS (Expected: 9)" -ForegroundColor Red
}

# 3. MapReduce Output
Write-Host "`n[3/$totalChecks] Checking MapReduce Outputs on HDFS..." -ForegroundColor Yellow
$mr01 = docker exec namenode hdfs dfs -test -e /data/olist/output/mr01/_SUCCESS 2>$null; $r1 = $LASTEXITCODE
$mr02 = docker exec namenode hdfs dfs -test -e /data/olist/output/mr02/_SUCCESS 2>$null; $r2 = $LASTEXITCODE
$mr03 = docker exec namenode hdfs dfs -test -e /data/olist/output/mr03/_SUCCESS 2>$null; $r3 = $LASTEXITCODE

if ($r1 -eq 0 -and $r2 -eq 0 -and $r3 -eq 0) {
    Write-Host "  PASS: MapReduce MR01, MR02, MR03 outputs verified with _SUCCESS on HDFS" -ForegroundColor Green
    $passedChecks++
} else {
    Write-Host "  FAIL: Missing MapReduce _SUCCESS flags (MR01: $r1, MR02: $r2, MR03: $r3)" -ForegroundColor Red
}

# 4. Spark Enriched Parquet Table
Write-Host "`n[4/$totalChecks] Checking Spark Enriched Parquet on HDFS..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -test -e /data/olist/processed/orders_enriched.parquet/_SUCCESS 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  PASS: Spark partitioned Parquet table verified with _SUCCESS on HDFS" -ForegroundColor Green
    $passedChecks++
} else {
    Write-Host "  FAIL: Spark Parquet dataset missing on HDFS" -ForegroundColor Red
}

# 5. MongoDB Document Count
Write-Host "`n[5/$totalChecks] Checking MongoDB Document Collection..." -ForegroundColor Yellow
try {
    $mongoCount = python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)['olist_db']['orders'].count_documents({}))" 2>$null
    if ([int]$mongoCount -gt 90000) {
        Write-Host "  PASS: MongoDB 'orders' collection contains $mongoCount documents" -ForegroundColor Green
        $passedChecks++
    } else {
        Write-Host "  FAIL: MongoDB count is $mongoCount (Expected > 90,000)" -ForegroundColor Red
    }
} catch {
    Write-Host "  FAIL: Could not query MongoDB: $_" -ForegroundColor Red
}

# 6. Elasticsearch Document Count
Write-Host "`n[6/$totalChecks] Checking Elasticsearch Index..." -ForegroundColor Yellow
try {
    $esResp = Invoke-RestMethod -Uri "http://localhost:9200/olist_analytics/_count" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($esResp.count -gt 100000) {
        Write-Host "  PASS: Elasticsearch index 'olist_analytics' contains $($esResp.count) documents" -ForegroundColor Green
        $passedChecks++
    } else {
        Write-Host "  FAIL: Elasticsearch document count is $($esResp.count) (Expected > 100,000)" -ForegroundColor Red
    }
} catch {
    Write-Host "  FAIL: Could not query Elasticsearch index: $_" -ForegroundColor Red
}

# 7. Dashboard Endpoint
Write-Host "`n[7/$totalChecks] Checking Dashboard Endpoint..." -ForegroundColor Yellow
$dashRunning = docker inspect -f '{{.State.Running}}' dashboard 2>$null
if ($dashRunning -eq "true") {
    Write-Host "  PASS: Dashboard container is running on http://localhost:8501" -ForegroundColor Green
    $passedChecks++
} else {
    Write-Host "  INFO: Dashboard container not running (run 'docker compose up -d dashboard' or 'streamlit run dashboard/app.py')" -ForegroundColor Yellow
}

Write-Host "`n================ VERIFICATION SUMMARY ================" -ForegroundColor Cyan
Write-Host " Passed: $passedChecks / $totalChecks verification checks" -ForegroundColor $(if ($passedChecks -ge 6) { "Green" } else { "Red" })
Write-Host "======================================================" -ForegroundColor Cyan

if ($passedChecks -ge 6) {
    exit 0
} else {
    exit 1
}
