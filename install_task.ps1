$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "CityHeavenMonitor"
$runnerScript = Join-Path $projectRoot "run_check.ps1"
$powerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$taskCommand = "`"$powerShell`" -NoProfile -ExecutionPolicy Bypass -File `"$runnerScript`""

schtasks.exe /Create /TN $taskName /SC MINUTE /MO 15 /TR $taskCommand /F | Out-Null
Write-Output "Scheduled task '$taskName' created. It will run every 15 minutes."