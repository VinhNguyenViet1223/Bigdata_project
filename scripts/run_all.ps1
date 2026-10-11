# scripts/run_all.ps1
# Runs all 6 MapReduce jobs sequentially, benchmarks execution times, and validates outputs.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " [HADOOP MAPREDUCE] Running Full Batch Pipeline  " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Run local unit tests first
Write-Host "--> Step 1: Running unit test suite..." -ForegroundColor Yellow
python (Join-Path $PSScriptRoot "..\tests\run_all_tests.py")
if ($LASTEXITCODE -ne 0) {
    Write-Error "Unit tests failed! Aborting MapReduce execution."
    exit 1
}
Write-Host "  [OK] All unit tests passed!" -ForegroundColor Green

# 2. Run MapReduce jobs 1 through 6
$metrics = @()

for ($j = 1; $j -le 6; $j++) {
    Write-Host "`n>>> Starting Job $j / 6..." -ForegroundColor Cyan
    $t0 = Get-Date
    & (Join-Path $PSScriptRoot "run_job.ps1") -Job $j
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Execution failed at Job $j!"
        exit 1
    }
    $t1 = Get-Date
    $elapsed = ($t1 - $t0).TotalSeconds
    $metrics += [PSCustomObject]@{
        Job = "Job $j"
        DurationSeconds = [Math]::Round($elapsed, 2)
    }
}

Write-Host "`n================ PIPELINE BENCHMARK SUMMARY ================" -ForegroundColor Cyan
$metrics | Format-Table -AutoSize

# 3. Collect evidence
Write-Host "--> Step 3: Collecting real Hadoop evidence to evidence/..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "collect_evidence.ps1")

Write-Host "`n[SUCCESS] Entire 6-Job Hadoop MapReduce pipeline finished successfully!" -ForegroundColor Green
