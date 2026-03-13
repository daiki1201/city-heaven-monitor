$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$logsDir = Join-Path $projectRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$logPath = Join-Path $logsDir "city_heaven.log"
$python = "python"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logPath -Value "[$timestamp] Starting city_heaven check"

& $python "main.py" "--once" *>> $logPath
$exitCode = $LASTEXITCODE

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logPath -Value "[$timestamp] Finished city_heaven check (exit=$exitCode)"

exit $exitCode