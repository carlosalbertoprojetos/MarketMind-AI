$root = Split-Path -Parent $PSScriptRoot
$localDir = Join-Path $root ".local"
if (-not (Test-Path $localDir)) { New-Item -ItemType Directory -Path $localDir | Out-Null }
$logOut = Join-Path $localDir "backend-validate.out.log"
$logErr = Join-Path $localDir "backend-validate.err.log"
$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8003/api/v1"
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
    $script:backendProcess = Start-Process -FilePath "py" -ArgumentList "-3.10","-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8003" -WorkingDirectory (Join-Path $root "backend") -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
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
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/register" -ContentType "application/json" -Body $registerPayload -ErrorAction Stop
} catch { Write-Output "AUTH_REGISTER=FAIL"; Write-ErrorResponse $_; throw }

$loginPayload = @{ email = $email; password = $password } | ConvertTo-Json
$login = try {
  Invoke-RestMethod -Method Post -Uri "$baseUrl/auth/login" -ContentType "application/json" -Body $loginPayload -ErrorAction Stop
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

  $campaignPayload = @{
    workspace_id = $workspace.id
    product_id = $product.id
    name = "Smoke Campaign"
    objective = "Validar campanha e sequencia de conteudo"
  } | ConvertTo-Json
  $campaignPlan = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/campaign/plan" -Headers $headers -ContentType "application/json" -Body $campaignPayload

  $contentTypes = @("linkedin_post","instagram_post","x_thread","youtube_script","carousel","email_campaign")
  $generated = @()
  foreach ($ctype in $contentTypes) {
    $contentPayload = @{
      product_id = $product.id
      content_type = $ctype
      brief = "Gerar conteudo $ctype para validar multi-formato."
    } | ConvertTo-Json
    $item = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/content/generate" -Headers $headers -ContentType "application/json" -Body $contentPayload
    $generated += $item.id
  }

  Write-Output ("HEALTH=OK AUTH=OK CAMPAIGN={0} CONTENT_ITEMS={1}" -f $campaignPlan.campaign_id, ($generated -join ","))
} catch {
  Write-Output "CAMPAIGN_CONTENT=FAIL"
  Write-ErrorResponse $_
  if (Test-Path $logOut) { Get-Content $logOut -Tail 200 }
  if (Test-Path $logErr) { Get-Content $logErr -Tail 200 }
  if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
  exit 1
}

if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
