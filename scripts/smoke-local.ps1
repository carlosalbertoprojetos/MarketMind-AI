$root = Split-Path -Parent $PSScriptRoot

$backend = Start-Process -FilePath "py" -ArgumentList "-3","-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $root "backend") -PassThru
$frontend = Start-Process -FilePath "cmd" -ArgumentList "/c","npm","run","dev","--","--hostname","127.0.0.1","--port","3000" -WorkingDirectory (Join-Path $root "frontend") -PassThru

Start-Sleep -Seconds 12

$backendStatus = "ERR"
$frontendStatus = "ERR"

try { $backendStatus = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/api/v1/health").StatusCode } catch { }
try { $frontendStatus = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:3000").StatusCode } catch { }

Write-Output ("BACKEND={0} FRONTEND={1}" -f $backendStatus, $frontendStatus)

if ($backend -and !$backend.HasExited) { Stop-Process -Id $backend.Id -Force }
if ($frontend -and !$frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }