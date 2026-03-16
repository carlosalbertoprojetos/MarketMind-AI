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
if (-not $token) { throw "No access token" }
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

  $contentPayload = @{
    product_id = $product.id
    content_type = "linkedin_post"
    brief = "Seed analytics event"
  } | ConvertTo-Json
  $content = Invoke-RestMethod -Method Post -Uri "$baseUrl/ai/content/generate" -Headers $headers -ContentType "application/json" -Body $contentPayload

  $postPayload = @{
    content_item_id = $content.id
    platform = "linkedin"
    status = "published"
    url = "https://example.com/post"
  } | ConvertTo-Json
  $post = Invoke-RestMethod -Method Post -Uri "$baseUrl/posts/" -Headers $headers -ContentType "application/json" -Body $postPayload

  $now = (Get-Date).ToString("o")
  $events = @(
    @{ post_id = $post.id; event_type = "post_published"; occurred_at = $now; metadata = @{ source = "seed" } },
    @{ post_id = $post.id; event_type = "post_viewed"; occurred_at = $now; metadata = @{ source = "seed" } },
    @{ post_id = $post.id; event_type = "post_clicked"; occurred_at = $now; metadata = @{ source = "seed" } },
    @{ post_id = $post.id; event_type = "post_engaged"; occurred_at = $now; metadata = @{ source = "seed" } }
  )

  foreach ($evt in $events) {
    $payload = $evt | ConvertTo-Json
    $null = Invoke-RestMethod -Method Post -Uri "$baseUrl/analytics/events" -Headers $headers -ContentType "application/json" -Body $payload
  }

  $summary = Invoke-RestMethod -Method Get -Uri "$baseUrl/ai/analytics/summary" -Headers $headers
  Write-Output ("ANALYTICS_SUMMARY=OK engagement_rate={0} ctr={1} growth={2}" -f $summary.engagement_rate, $summary.ctr, $summary.growth)
} catch {
  Write-Output "ANALYTICS_SEED=FAIL"
  Write-ErrorResponse $_
  if (Test-Path $logOut) { Get-Content $logOut -Tail 200 }
  if (Test-Path $logErr) { Get-Content $logErr -Tail 200 }
  if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
  exit 1
}

if ($startedBackend -and $backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
