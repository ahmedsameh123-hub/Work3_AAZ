# Opens backend in a new PowerShell window (stays open even if IDE terminal closes)
param(
    [switch]$Reload,
    [switch]$HostAll,
    [int]$Port = 8000
)

$here = $PSScriptRoot
$flags = @()
if ($Reload) { $flags += "-Reload" }
if ($HostAll) { $flags += "-HostAll" }
if ($Port -ne 8000) { $flags += "-Port"; $flags += "$Port" }

$argList = @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $here "start.ps1")) + $flags
Start-Process -FilePath "powershell.exe" -ArgumentList $argList -WorkingDirectory $here

Write-Host "Backend starting in a new window..."
Write-Host "Health check: http://127.0.0.1:$Port/api/health"
