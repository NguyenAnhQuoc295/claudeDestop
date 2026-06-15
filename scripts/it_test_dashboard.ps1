param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [string]$ApiKey = "dev-secret",
    [switch]$SkipBrowser,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$DashboardDir = Join-Path $Root "dashboard-ui"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$OutLog = Join-Path $BackendDir "it_test_uvicorn.out.log"
$ErrLog = Join-Path $BackendDir "it_test_uvicorn.err.log"
$Url = "http://$HostAddress`:$Port/"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Wait-ForHealth($HealthUrl) {
    for ($i = 1; $i -le 30; $i++) {
        try {
            $result = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 2
            if ($result.status -eq "ok") {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

if ($CheckOnly) {
    Write-Host "PowerShell script parsed successfully."
    exit 0
}

Write-Step "Checking required folders"
if (-not (Test-Path $BackendDir)) {
    throw "Missing backend folder: $BackendDir"
}
if (-not (Test-Path $DashboardDir)) {
    throw "Missing dashboard-ui folder: $DashboardDir"
}

Write-Step "Checking port $Port"
$listeners = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" -and $_.OwningProcess -and $_.OwningProcess -ne 0 } |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($listeners) {
    Write-Host "Port $Port is already used by process: $($listeners -join ', ')" -ForegroundColor Yellow
    $answer = Read-Host "Stop these process(es) and continue? Type Y to confirm"
    if ($answer -notin @("Y", "y")) {
        Write-Host "Cancelled. Please close the existing app or choose another port."
        exit 1
    }

    foreach ($owner in $listeners) {
        Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

Write-Step "Preparing Python virtual environment"
if (-not (Test-Path $VenvPython)) {
    python -m venv (Join-Path $BackendDir ".venv")
}

Write-Step "Installing backend dependencies"
& $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")

Write-Step "Building dashboard-ui"
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js LTS first."
}

Push-Location $DashboardDir
try {
    npm install
    npm run build
} finally {
    Pop-Location
}

Write-Step "Starting backend"
$env:PROMPT_LOG_API_KEY = $ApiKey

Remove-Item -LiteralPath $OutLog, $ErrLog -ErrorAction SilentlyContinue

$process = Start-Process `
    -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", $HostAddress, "--port", "$Port") `
    -WorkingDirectory $BackendDir `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

$healthUrl = "http://$HostAddress`:$Port/health"
if (-not (Wait-ForHealth $healthUrl)) {
    Write-Host "Backend did not become ready. Last error log:" -ForegroundColor Red
    Get-Content $ErrLog -ErrorAction SilentlyContinue | Select-Object -Last 40
    exit 1
}

Write-Step "Running API checks"
$health = Invoke-RestMethod -Uri $healthUrl
$summary = Invoke-RestMethod -Uri "http://$HostAddress`:$Port/api/dashboard/summary"

Write-Host "Health: $($health.status)" -ForegroundColor Green
Write-Host "Total prompts: $($summary.total_prompts)"
Write-Host "Employees: $($summary.unique_employees)"
Write-Host "Projects: $($summary.unique_projects)"
Write-Host "Backend PID: $($process.Id)"

if (-not $SkipBrowser) {
    Write-Step "Opening dashboard"
    Start-Process $Url
}

Write-Host ""
Write-Host "Ready for IT test:" -ForegroundColor Green
Write-Host "Dashboard: $Url"
Write-Host "Health:    $healthUrl"
Write-Host ""
Write-Host "To stop backend later, run:"
Write-Host "Stop-Process -Id $($process.Id)"
