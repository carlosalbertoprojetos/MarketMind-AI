param(
  [Parameter(Mandatory=$true)]
  [string]$AdminUser,
  [Parameter(Mandatory=$true)]
  [string]$AdminPassword
)

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root "backend\\.env"

if (-not (Test-Path $envFile)) {
  Write-Error "Nao encontrei o arquivo .env em $envFile"
  exit 1
}

$kv = @{}
Get-Content $envFile | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  if ($_ -match '^\s*([^=]+)=(.*)$') {
    $key = $matches[1].Trim()
    $val = $matches[2].Trim()
    if ($val.StartsWith('\"') -and $val.EndsWith('\"')) {
      $val = $val.Trim('\"')
    }
    if ($val.StartsWith("'") -and $val.EndsWith("'")) {
      $val = $val.Trim("'")
    }
    $kv[$key] = $val
  }
}

$dbHost = $kv["DB_HOST"]
$dbPort = $kv["DB_PORT"]
$dbName = $kv["DB_NAME"]
$dbUser = $kv["DB_USER"]
$dbPassword = $kv["DB_PASSWORD"]

if (-not $dbHost -or -not $dbPort -or -not $dbName -or -not $dbUser -or -not $dbPassword) {
  Write-Error "Variaveis DB_* incompletas no backend/.env"
  exit 1
}

$dbUserSql = $dbUser.Replace("'", "''")
$dbNameSql = $dbName.Replace("'", "''")
$dbPasswordSql = $dbPassword.Replace("'", "''")

$env:PGPASSWORD = $AdminPassword

$roleExists = psql -w -h $dbHost -p $dbPort -U $AdminUser -d postgres -tA -c "SELECT 1 FROM pg_roles WHERE rolname='$dbUserSql';"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $roleExists) {
  psql -w -h $dbHost -p $dbPort -U $AdminUser -d postgres -c "CREATE ROLE `"$dbUser`" LOGIN PASSWORD '$dbPasswordSql';"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$dbExists = psql -w -h $dbHost -p $dbPort -U $AdminUser -d postgres -tA -c "SELECT 1 FROM pg_database WHERE datname='$dbNameSql';"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $dbExists) {
  psql -w -h $dbHost -p $dbPort -U $AdminUser -d postgres -c "CREATE DATABASE `"$dbName`" OWNER `"$dbUser`";"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

psql -w -h $dbHost -p $dbPort -U $AdminUser -d $dbName -c "CREATE EXTENSION IF NOT EXISTS vector;"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Banco pronto: $dbName (owner: $dbUser)"
