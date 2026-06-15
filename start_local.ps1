param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [string]$ApiKey = "dev-secret",
    [switch]$BuildDashboard,
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$DashboardDir = Join-Path $Root "dashboard-ui"
$DashboardDist = Join-Path $DashboardDir "dist"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating backend virtual environment..."
    python -m venv (Join-Path $BackendDir ".venv")
}

Write-Host "Installing backend dependencies..."
& $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")

if ($BuildDashboard) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "npm was not found. Install Node.js LTS before building dashboard-ui."
        exit 1
    }

    Write-Host "Installing dashboard dependencies..."
    Push-Location $DashboardDir
    try {
        npm install
        Write-Host "Building dashboard-ui..."
        npm run build
    } finally {
        Pop-Location
    }
}

$listeners = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" -and $_.OwningProcess -and $_.OwningProcess -ne 0 } |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($listeners -and $ForceRestart) {
    foreach ($owner in $listeners) {
        Write-Host "Stopping process $owner on port $Port..."
        Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
} elseif ($listeners) {
    Write-Host "Port $Port is already in use by process: $($listeners -join ', ')"
    Write-Host "Run with -ForceRestart to stop it automatically."
    exit 1
}

$env:PROMPT_LOG_API_KEY = $ApiKey

Write-Host "Starting Claude Logger backend..."
Write-Host "API health: http://$HostAddress`:$Port/health"
if (Test-Path (Join-Path $DashboardDist "index.html")) {
    Write-Host "Dashboard:  http://$HostAddress`:$Port/"
} else {
    Write-Host "Dashboard UI has not been built into dashboard-ui/dist."
    Write-Host "Dev UI:     cd dashboard-ui; npm install; npm run dev"
    Write-Host "Prod UI:    .\start_local.ps1 -BuildDashboard"
}

Push-Location $BackendDir
try {
    & $VenvPython -m uvicorn app.main:app --reload --host $HostAddress --port $Port
} finally {
    Pop-Location
}
