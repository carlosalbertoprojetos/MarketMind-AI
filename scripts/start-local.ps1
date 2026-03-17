$root = Split-Path -Parent $PSScriptRoot
$localDir = Join-Path $root ".local"
$pidsFile = Join-Path $localDir "pids.json"

$backend = Start-Process -FilePath "py" -ArgumentList "-3.10","-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8003" -WorkingDirectory (Join-Path $root "backend") -PassThru
$frontend = Start-Process -FilePath "cmd" -ArgumentList "/c","npm","run","dev","--","--hostname","127.0.0.1","--port","3000" -WorkingDirectory (Join-Path $root "frontend") -PassThru

@{
  backend = $backend.Id
  frontend = $frontend.Id
} | ConvertTo-Json | Set-Content -Path $pidsFile

Write-Output "Backend PID: $($backend.Id)"
Write-Output "Frontend PID: $($frontend.Id)"
Write-Output "URLs: http://127.0.0.1:8003/api/v1/health and http://127.0.0.1:3000"
