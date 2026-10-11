# scripts/start.ps1
# Starts all Big Data ecosystem services via Docker Compose and verifies health.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " [DOCKER] Starting Big Data Ecosystem Services   " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Start containers
Set-Location (Join-Path $PSScriptRoot "..")
Write-Host "--> Running 'docker compose up -d'..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start Docker containers!"
    exit 1
}

# 2. Wait for services to stabilize
Write-Host "--> Waiting 5 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Check service statuses
$services = @("namenode", "datanode", "spark-master", "spark-worker", "mongodb", "elasticsearch", "mapreduce")

Write-Host "`n================ SERVICE STATUS AUDIT ================" -ForegroundColor Cyan
$allHealthy = $true

foreach ($svc in $services) {
    $running = docker inspect -f '{{.State.Running}}' $svc 2>$null
    if ($running -eq "true") {
        Write-Host "  [ONLINE]  $svc is running" -ForegroundColor Green
    } else {
        Write-Host "  [OFFLINE] $svc is NOT running" -ForegroundColor Red
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-Warning "Some services failed to start. Review logs via 'docker logs <container>'."
    exit 1
}

Write-Host "`n================ ACCESS ENDPOINTS & PORTS ================" -ForegroundColor Cyan
Write-Host "  HDFS NameNode Web UI:       http://localhost:9870" -ForegroundColor White
Write-Host "  HDFS RPC Endpoint:          hdfs://localhost:9000" -ForegroundColor White
Write-Host "  Spark Master Web UI:        http://localhost:8080" -ForegroundColor White
Write-Host "  Spark Worker Web UI:        http://localhost:8081" -ForegroundColor White
Write-Host "  MongoDB NoSQL Endpoint:     mongodb://localhost:27017" -ForegroundColor White
Write-Host "  Elasticsearch REST API:     http://localhost:9200" -ForegroundColor White
Write-Host "  Analytics Dashboard UI:     http://localhost:8501" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] All ecosystem containers started successfully!" -ForegroundColor Green
