$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    & $Command @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Command"
    }
}

try {
    Set-Location -LiteralPath $PSScriptRoot

    $pythonPath = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw "Python environment not found. Create .venv first."
    }

    $env:AWS_ACCESS_KEY_ID = "test"
    $env:AWS_SECRET_ACCESS_KEY = "test"
    $env:AWS_DEFAULT_REGION = "us-east-1"
    $env:S3_ENDPOINT_URL = "http://localhost:4566"
    $env:INPUT_FILE_PATTERN = "s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    $env:OUTPUT_FILE_PATTERN = "s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"

    Write-Host "Running unit tests..."
    Invoke-Checked -Command $pythonPath -Arguments @(
        "-m", "pytest", "tests", "-v"
    )

    Write-Host "Starting LocalStack..."
    Invoke-Checked -Command "docker" -Arguments @(
        "compose", "up", "--wait", "--wait-timeout", "120"
    )

    Write-Host "Checking test bucket..."
    $bucketName = Invoke-Checked -Command "docker" -Arguments @(
        "compose", "exec", "-T", "localstack",
        "aws", "--endpoint-url=http://localhost:4566",
        "s3api", "list-buckets",
        "--query", "Buckets[?Name=='nyc-duration'].Name",
        "--output", "text"
    )

    if ($bucketName -ne "nyc-duration") {
        Invoke-Checked -Command "docker" -Arguments @(
            "compose", "exec", "-T", "localstack",
            "aws", "--endpoint-url=http://localhost:4566",
            "s3", "mb", "s3://nyc-duration"
        )
    }

    Write-Host "Running integration test..."
    Invoke-Checked -Command $pythonPath -Arguments @(
        "integration_test.py"
    )

    Write-Host "All tests PASSED" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "Tests FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}