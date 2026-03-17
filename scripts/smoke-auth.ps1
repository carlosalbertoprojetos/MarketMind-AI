$root = Split-Path -Parent $PSScriptRoot
$localDir = Join-Path $root ".local"
if (-not (Test-Path $localDir)) { New-Item -ItemType Directory -Path $localDir | Out-Null }
$logOut = Join-Path $localDir "backend-smoke.out.log"
$logErr = Join-Path $localDir "backend-smoke.err.log"

$baseUrl = "http://127.0.0.1:8003/api/v1"
$backendProcess = $null
$startedBackend = $false

function Try-Request($script) {
  try { return & $script } catch { return $null }
}

function Write-ErrorResponse($err) {
  if ($err -and $err.Exception -and $err.Exception.Response) {
    try {
      $reader = New-Object System.IO.StreamReader($err.Exception.Response.GetResponseStream())
      $body = $reader.ReadToEnd()
      if ($body) { Write-Output $body }
    } catch {
      Write-Output $err
    }
  } else {
    Write-Output $err
  }
}

$health = Try-Request { Invoke-WebRequest -UseBasicParsing "$baseUrl/health" }
if (-not $health) {
  $portOpen = $false
  try {
    $portOpen = (Test-NetConnection -ComputerName 127.0.0.1 -Port 5432 -WarningAction SilentlyContinue).TcpTestSucceeded
  } catch { $portOpen = $false }

  if (-not $portOpen) {
    Write-Output "Postgres not reachable on 127.0.0.1:5432. Start your DB first."
    exit 0
  }

  $backendProcess = Start-Process -FilePath "py" -ArgumentList "-3.10","-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8003" -WorkingDirectory "backend" -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
  $startedBackend = $true
  Start-Sleep -Seconds 6
}

$random = [guid]::NewGuid().ToString("N").Substring(0, 8)
$orgSlug = "smoke-$random"
$email = "smoke-$random@marketmind.ai"
$password = "Secret123!"

$registerPayload = @{
  organization_name = "Smoke Org"
  organization_slug = $orgSlug
  full_name = "Smoke User"
  email = $email
  password = $password
} | ConvertTo-Json

$registerError = $null
$register = try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/register" -ContentType "application/json" -Body $registerPayload -ErrorAction Stop
} catch { $registerError = $_; $null }

if (-not $register) {
  Write-Output "Register failed"
  Write-ErrorResponse $registerError
  if (Test-Path $logOut) { Get-Content $logOut -Tail 200 }
  if (Test-Path $logErr) { Get-Content $logErr -Tail 200 }
  if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
  exit 1
}

$loginPayload = @{ email = $email; password = $password } | ConvertTo-Json
$loginError = $null
$login = try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/login" -ContentType "application/json" -Body $loginPayload -ErrorAction Stop
} catch { $loginError = $_; $null }

if (-not $login) {
  Write-Output "Login failed"
  Write-ErrorResponse $loginError
  if (Test-Path $logOut) { Get-Content $logOut -Tail 200 }
  if (Test-Path $logErr) { Get-Content $logErr -Tail 200 }
  if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
  exit 1
}

$token = $login.access_token
$me = Try-Request {
  Invoke-RestMethod -Method Get -Uri "$baseUrl/users/me" -Headers @{ Authorization = "Bearer $token" }
}

if ($me) {
  Write-Output "AUTH_SMOKE=OK email=$($me.email)"
} else {
  Write-Output "AUTH_SMOKE=FAIL"
}

if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
