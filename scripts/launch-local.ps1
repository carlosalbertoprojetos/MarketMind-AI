param(
  [string]$RootPath
)

$ErrorActionPreference = 'Stop'

function Stop-LocalProcess {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId
  )

  if ($ProcessId -le 0) {
    return
  }

  try {
    cmd /c taskkill /PID $ProcessId /T /F | Out-Null
  } catch {
  }
}

function Wait-LocalPort {
  param(
    [Parameter(Mandatory = $true)]
    [int]$Port,
    [Parameter(Mandatory = $true)]
    [int]$TimeoutSeconds,
    [int]$ProcessId = 0
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) {
      return $true
    }

    if ($ProcessId -gt 0) {
      $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
      if (-not $process) {
        return $false
      }
    }

    Start-Sleep -Milliseconds 500
  }

  return $false
}

if (-not $RootPath) {
  $RootPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

$backendScript = Join-Path $RootPath 'scripts\run-backend.bat'
$frontendScript = Join-Path $RootPath 'scripts\run-frontend.bat'
$localDir = Join-Path $RootPath '.local'
$frontendUrl = 'http://127.0.0.1:5173'
$browserProfileDir = Join-Path $localDir 'browser-profile'

if (-not (Test-Path $backendScript)) {
  throw "Script do backend nao encontrado em '$backendScript'."
}

if (-not (Test-Path $frontendScript)) {
  throw "Script do frontend nao encontrado em '$frontendScript'."
}

New-Item -ItemType Directory -Force $localDir | Out-Null
New-Item -ItemType Directory -Force $browserProfileDir | Out-Null

$pidFiles = @{
  backend = Join-Path $localDir 'backend-window.pid'
  frontend = Join-Path $localDir 'frontend-window.pid'
  browser = Join-Path $localDir 'browser.pid'
}

foreach ($file in $pidFiles.Values) {
  if (Test-Path $file) { Remove-Item $file -Force -ErrorAction SilentlyContinue }
}

$backendWindow = $null
$frontendWindow = $null
$browserProcess = $null

try {
  $backendWindow = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/k', "`"$backendScript`"") -WorkingDirectory $RootPath -PassThru
  Set-Content -Path $pidFiles.backend -Value $backendWindow.Id
  if (-not (Wait-LocalPort -Port 8003 -TimeoutSeconds 20 -ProcessId $backendWindow.Id)) {
    throw 'Backend nao ficou disponivel na porta 8003.'
  }

  $frontendWindow = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/k', "`"$frontendScript`"") -WorkingDirectory $RootPath -PassThru
  Set-Content -Path $pidFiles.frontend -Value $frontendWindow.Id
  if (-not (Wait-LocalPort -Port 5173 -TimeoutSeconds 30 -ProcessId $frontendWindow.Id)) {
    throw 'Frontend nao ficou disponivel na porta 5173.'
  }

  $browserCandidates = @(
    @{ Path = Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'; Args = @('--new-window', "--app=$frontendUrl", "--user-data-dir=$browserProfileDir") },
    @{ Path = Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'; Args = @('--new-window', "--app=$frontendUrl", "--user-data-dir=$browserProfileDir") },
    @{ Path = Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'; Args = @('--new-window', "--app=$frontendUrl", "--user-data-dir=$browserProfileDir") }
  )

  foreach ($candidate in $browserCandidates) {
    if ($candidate.Path -and (Test-Path $candidate.Path)) {
      $browserProcess = Start-Process -FilePath $candidate.Path -ArgumentList $candidate.Args -PassThru
      break
    }
  }

  if ($browserProcess) {
    Set-Content -Path $pidFiles.browser -Value $browserProcess.Id
  } else {
    Start-Process -FilePath $frontendUrl | Out-Null
  }
} catch {
  if ($browserProcess) {
    Stop-LocalProcess -ProcessId $browserProcess.Id
  }
  if ($frontendWindow) {
    Stop-LocalProcess -ProcessId $frontendWindow.Id
  }
  if ($backendWindow) {
    Stop-LocalProcess -ProcessId $backendWindow.Id
  }

  foreach ($file in $pidFiles.Values) {
    if (Test-Path $file) {
      Remove-Item $file -Force -ErrorAction SilentlyContinue
    }
  }

  throw
}
