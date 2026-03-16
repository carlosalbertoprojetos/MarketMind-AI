$root = Split-Path -Parent $PSScriptRoot
$pidsFile = Join-Path $root ".local\pids.json"

if (-Not (Test-Path $pidsFile)) {
  Write-Output "No PID file found at $pidsFile"
  exit 0
}

$pids = Get-Content $pidsFile | ConvertFrom-Json

foreach ($name in $pids.PSObject.Properties.Name) {
  $procId = $pids.$name
  try {
    Stop-Process -Id $procId -Force -ErrorAction Stop
    Write-Output "Stopped $name (PID $procId)"
  } catch {
    Write-Output "Could not stop $name (PID $procId)"
  }
}

Remove-Item $pidsFile -ErrorAction SilentlyContinue
