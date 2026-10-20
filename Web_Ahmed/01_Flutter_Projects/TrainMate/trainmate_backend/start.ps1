# TrainMate backend — reliable local start (OneDrive-safe defaults)
param(
    [switch]$Reload,
    [switch]$HostAll,
    [int]$Port = 8000
)

Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "Installing core dependencies..."
& $py -m pip install --upgrade pip -q
& $py -m pip install -r requirements.txt -q

if (-not (Test-Path ".env")) {
    Write-Host "Copying .env.example -> .env"
    Copy-Item ".env.example" ".env"
}

$hostAddr = if ($HostAll) { "0.0.0.0" } else { "127.0.0.1" }

# Warn if something already listens on the port
try {
    $inUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($inUse) {
        $pid = ($inUse | Select-Object -First 1).OwningProcess
        Write-Host ""
        Write-Host "WARNING: Port $Port is already in use (PID $pid)." -ForegroundColor Yellow
        Write-Host "Stop that process first, or run: .\start.ps1 -Port 8001"
        Write-Host ""
    }
} catch {
    # Get-NetTCPConnection may be unavailable on some SKUs — ignore
}

Write-Host ""
Write-Host "Starting TrainMate API"
Write-Host "  URL:    http://${hostAddr}:$Port"
Write-Host "  Health: http://127.0.0.1:${Port}/api/health"
Write-Host ""
Write-Host "Tips:"
Write-Host "  - Keep this terminal open while the app runs."
Write-Host "  - Do NOT press Ctrl+C unless you want to stop the server."
Write-Host "  - For a phone on Wi‑Fi use: .\start.ps1 -HostAll"
Write-Host "  - --reload is OFF by default (OneDrive sync can restart/kill the server)."
Write-Host ""

$uvicornArgs = @(
    "-m", "uvicorn", "app.main:app",
    "--host", $hostAddr,
    "--port", "$Port"
)

if ($Reload) {
    Write-Host "Reload enabled (watching app/ only)." -ForegroundColor Yellow
    $uvicornArgs += @(
        "--reload",
        "--reload-dir", "app",
        "--reload-exclude", "*.db",
        "--reload-exclude", ".venv"
    )
}

Write-Host "Command: $py $($uvicornArgs -join ' ')"
Write-Host ""

& $py @uvicornArgs
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "Server stopped (exit 0). If you did not press Ctrl+C, another program may have closed it." -ForegroundColor Yellow
} else {
    Write-Host "Server exited with code $code" -ForegroundColor Red
}
Read-Host "Press Enter to close this window"
