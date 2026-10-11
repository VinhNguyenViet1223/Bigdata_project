# scripts/run_job.ps1
# Runs a specific Hadoop Streaming MapReduce job (1 to 6) on the cluster.

param (
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateRange(1, 6)]
    [int]$Job
)

$ErrorActionPreference = "Stop"

$STREAMING_JAR = "/opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar"
$NN = "hdfs://namenode:9000"

$jobsMeta = @{
    1 = @{
        Name = "job01_order_statistics"
        Title = "Job 01: Order Statistics Distribution"
        Input = "$NN/data/olist/olist_orders_dataset.csv"
        Output = "$NN/output/job01_order_statistics"
        Mapper = "python3 /app/src/jobs/job01_order_statistics/mapper.py"
        Reducer = "python3 /app/src/jobs/job01_order_statistics/reducer.py"
        Files = @()
    }
    2 = @{
        Name = "job02_revenue"
        Title = "Job 02: Monthly Revenue & Trend (T10)"
        Input = "$NN/data/olist/olist_order_items_dataset.csv"
        Output = "$NN/output/job02_monthly_revenue"
        Mapper = "python3 /app/src/jobs/job02_revenue/mapper_monthly.py"
        Reducer = "python3 /app/src/jobs/job02_revenue/reducer_monthly.py"
        Files = @("-files", "/app/data/olist_orders_dataset.csv")
    }

    3 = @{
        Name = "job03_category"
        Title = "Job 03: Category Analysis (Multi-Table Join)"
        Input = "$NN/data/olist/olist_order_items_dataset.csv"
        Output = "$NN/output/job03_category"
        Mapper = "python3 /app/src/jobs/job03_category/mapper.py"
        Reducer = "python3 /app/src/jobs/job03_category/reducer.py"
        Files = @("-files", "/app/data/olist_products_dataset.csv,/app/data/product_category_name_translation.csv")
    }
    4 = @{
        Name = "job04_seller"
        Title = "Job 04: Seller Performance (Items, Revenue, Freight)"
        Input = "$NN/data/olist/olist_order_items_dataset.csv"
        Output = "$NN/output/job04_seller"
        Mapper = "python3 /app/src/jobs/job04_seller/mapper.py"
        Reducer = "python3 /app/src/jobs/job04_seller/reducer.py"
        Files = @()
    }
    5 = @{
        Name = "job05_reviews"
        Title = "Job 05: Customer Reviews Analysis (Score & Average)"
        Input = "$NN/data/olist/olist_order_reviews_dataset.csv"
        Output = "$NN/output/job05_reviews"
        Mapper = "python3 /app/src/jobs/job05_reviews/mapper.py"
        Reducer = "python3 /app/src/jobs/job05_reviews/reducer.py"
        Files = @()
    }
    6 = @{
        Name = "job06_delivery"
        Title = "Job 06: Delivery Logistics & Delay Analysis"
        Input = "$NN/data/olist/olist_orders_dataset.csv"
        Output = "$NN/output/job06_delivery"
        Mapper = "python3 /app/src/jobs/job06_delivery/mapper.py"
        Reducer = "python3 /app/src/jobs/job06_delivery/reducer.py"
        Files = @()
    }
}

$cfg = $jobsMeta[$Job]

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Running $($cfg.Title)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Clean previous output directory
Write-Host "--> Cleaning previous HDFS output: $($cfg.Output)..." -ForegroundColor Yellow
docker exec mapreduce hdfs dfs -rm -r -f $($cfg.Output) 2>$null

# 2. Build Hadoop Streaming arguments array
$hadoopArgs = @(
    "exec", "mapreduce",
    "hadoop", "jar", $STREAMING_JAR,
    "-D", "mapreduce.framework.name=local"
)

if ($cfg.Files.Count -gt 0) {
    $hadoopArgs += $cfg.Files
}

$hadoopArgs += @(
    "-input", $cfg.Input,
    "-output", $cfg.Output,
    "-mapper", $cfg.Mapper,
    "-reducer", $cfg.Reducer
)

Write-Host "--> Executing MapReduce on cluster..." -ForegroundColor Yellow
$startTime = Get-Date
& docker @hadoopArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "MapReduce execution failed for Job $Job!"
    exit 1
}
$duration = ((Get-Date) - $startTime).TotalSeconds

Write-Host "`n[SUCCESS] Job $Job completed in $($duration.ToString('F2')) seconds!" -ForegroundColor Green
Write-Host "`n================ OUTPUT PREVIEW (First 15 lines) ================" -ForegroundColor Cyan
docker exec namenode bash -c "hdfs dfs -cat '$($cfg.Output)/part-00000' 2>/dev/null | head -n 15"
$global:LASTEXITCODE = 0
