$root = Split-Path -Parent $PSScriptRoot
$localDir = Join-Path $root ".local"
if (-not (Test-Path $localDir)) { New-Item -ItemType Directory -Path $localDir | Out-Null }
$logOut = Join-Path $localDir "backend-validate.out.log"
$logErr = Join-Path $localDir "backend-validate.err.log"
$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8000/api/v1"
$backendProcess = $null
$startedBackend = $false

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

function Ensure-Backend {
  $health = $null
  try { $health = (Invoke-WebRequest -UseBasicParsing "$baseUrl/health").StatusCode } catch { $health = $null }
  if (-not $health) {
    $script:backendProcess = Start-Process -FilePath "py" -ArgumentList "-3","-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000" -WorkingDirectory (Join-Path $root "backend") -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
    $script:startedBackend = $true
    Start-Sleep -Seconds 6
  }
}

Ensure-Backend

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

$register = try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/register" -ContentType "application/json" -Body $registerPayload
} catch { Write-Output "AUTH_REGISTER=FAIL"; Write-ErrorResponse $_; throw }

$loginPayload = @{ email = $email; password = $password } | ConvertTo-Json
$login = try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/login" -ContentType "application/json" -Body $loginPayload
} catch { Write-Output "AUTH_LOGIN=FAIL"; Write-ErrorResponse $_; throw }

$token = $login.access_token
if (-not $token) {
  Write-Output "AUTH_TOKEN=FAIL"
  throw "No access token"
}
$headers = @{ Authorization = "Bearer $token" }

try {
  $workspacePayload = @{ name = "Smoke Workspace"; slug = "smoke-$random"; description = "Workspace smoke test" } | ConvertTo-Json
  $workspace = Invoke-RestMethod -Method Post -Uri "$baseUrl/workspaces/" -Headers $headers -ContentType "application/json" -Body $workspacePayload

  $brandPayload = @{ workspace_id = $workspace.id; name = "Smoke Brand"; description = "Brand smoke test"; website_url = "https://example.com" } | ConvertTo-Json
  $brand = Invoke-RestMethod -Method Post -Uri "$baseUrl/brands/" -Headers $headers -ContentType "application/json" -Body $brandPayload

  $productPayload = @{
    brand_id = $brand.id
    name = "Smoke Product"
    description = "Product smoke test"
    website_url = "https://example.com"
    status = "active"
  } | ConvertTo-Json
  $product = Invoke-RestMethod -Method Post -Uri "$baseUrl/products/" -Headers $headers -ContentType "application/json" -Body $productPayload

  $audiencePayload = @{ product_id = $product.id; count = 2 } | ConvertTo-Json
  $personas = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/audience/generate" -Headers $headers -ContentType "application/json" -Body $audiencePayload

  $personaId = $personas[0].id
  $narrativePayload = @{ product_id = $product.id; persona_id = $personaId } | ConvertTo-Json
  $narrative = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/narrative/generate" -Headers $headers -ContentType "application/json" -Body $narrativePayload

  $contentPayload = @{
    product_id = $product.id
    persona_id = $personaId
    content_type = "linkedin_post"
    brief = "Validar fluxo de narrativa e audiencia."
  } | ConvertTo-Json
  $content = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/content/generate" -Headers $headers -ContentType "application/json" -Body $contentPayload

  $contentItems = Invoke-RestMethod -Method Get -Uri "$baseUrl/content-items/" -Headers $headers

  Write-Output ("HEALTH=OK AUTH=OK PERSONAS={0} NARRATIVE=OK CONTENT_ITEM={1} CONTENT_TOTAL={2}" -f $personas.Count, $content.id, $contentItems.Count)
} catch {
  Write-Output "AI_FLOW=FAIL"
  Write-ErrorResponse $_
  if (Test-Path $logOut) { Get-Content $logOut -Tail 200 }
  if (Test-Path $logErr) { Get-Content $logErr -Tail 200 }
  if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
  exit 1
}

if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
