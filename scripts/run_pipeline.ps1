# scripts/run_pipeline.ps1
# End-to-End Orchestrator for Olist Big Data Ecosystem Pipeline

$ErrorActionPreference = "Stop"

$startTime = Get-Date

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "         OLIST E-COMMERCE BIG DATA PIPELINE - END-TO-END ORCHESTRATION           " -ForegroundColor Cyan
Write-Host "  HDFS -> MapReduce -> Spark ETL & SQL -> MongoDB -> Elasticsearch -> Dashboard " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Pipeline Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Step 1: Start Docker Services
Write-Host "`n>>> [STEP 1/7] Starting Infrastructure Services via Docker Compose..." -ForegroundColor Magenta
& "$PSScriptRoot\start.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 1 Failed: Could not start Docker services!"
    exit 1
}

# Step 2: Initialize HDFS Storage Layer
Write-Host "`n>>> [STEP 2/7] Preparing HDFS Storage & Verifying Datasets..." -ForegroundColor Magenta
& "$PSScriptRoot\init_hdfs.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 2 Failed: HDFS initialization failed!"
    exit 1
}

# Step 3: Execute MapReduce Jobs
Write-Host "`n>>> [STEP 3/7] Running Hadoop Streaming MapReduce Jobs (MR01, MR02, MR03)..." -ForegroundColor Magenta
& "$PSScriptRoot\run_mapreduce.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 3 Failed: MapReduce job execution failed!"
    exit 1
}

# Step 4: Execute Apache Spark Processing
Write-Host "`n>>> [STEP 4/7] Submitting PySpark ETL, Spark SQL Analytics & Data Quality Jobs..." -ForegroundColor Magenta
& "$PSScriptRoot\run_spark.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 4 Failed: Spark job execution failed!"
    exit 1
}

# Step 5: Load MongoDB NoSQL Database
Write-Host "`n>>> [STEP 5/7] Loading Denormalized Documents & Aggregations into MongoDB..." -ForegroundColor Magenta
& "$PSScriptRoot\load_mongodb.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 5 Failed: MongoDB data loading failed!"
    exit 1
}

# Step 6: Load Elasticsearch Search Engine
Write-Host "`n>>> [STEP 6/7] Indexing Documents & Running Query Suite on Elasticsearch..." -ForegroundColor Magenta
& "$PSScriptRoot\load_elasticsearch.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 6 Failed: Elasticsearch indexing failed!"
    exit 1
}

# Step 7: Comprehensive System Verification
Write-Host "`n>>> [STEP 7/7] Running Full System Verification Audit..." -ForegroundColor Magenta
& "$PSScriptRoot\verify.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Step 7 Failed: System verification failed!"
    exit 1
}

$duration = (Get-Date) - $startTime

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "                END-TO-END PIPELINE COMPLETED SUCCESSFULLY!                     " -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Total Execution Time: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor White
Write-Host "`nAccess URLs for Demonstration:" -ForegroundColor Cyan
Write-Host "  * Analytics Web Dashboard: http://localhost:8501" -ForegroundColor Yellow
Write-Host "  * Apache Spark Web UI:     http://localhost:8080" -ForegroundColor Yellow
Write-Host "  * Hadoop HDFS Web UI:      http://localhost:9870" -ForegroundColor Yellow
Write-Host "  * Elasticsearch Endpoint:  http://localhost:9200" -ForegroundColor Yellow
Write-Host "  * MongoDB NoSQL Port:      localhost:27017" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Green
