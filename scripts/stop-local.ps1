param(
  [string]$RootPath
)

$ErrorActionPreference = 'SilentlyContinue'

if (-not $RootPath) {
  $RootPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

$localDir = Join-Path $RootPath '.local'
$pidFiles = @(
  Join-Path $localDir 'browser.pid',
  Join-Path $localDir 'frontend-window.pid',
  Join-Path $localDir 'backend-window.pid'
)

foreach ($pidFile in $pidFiles) {
  if (-not (Test-Path $pidFile)) { continue }
  $raw = Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
  $procId = 0
  if ([int]::TryParse(($raw -as [string]), [ref]$procId) -and $procId -gt 0) {
    cmd /c taskkill /PID $procId /T /F | Out-Null
  }
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

foreach ($port in @(8003, 5173)) {
  $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $connections) {
    if ($procId) {
      cmd /c taskkill /PID $procId /T /F | Out-Null
    }
  }
}
