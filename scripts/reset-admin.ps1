$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
$env:PYTHONPATH = "$root\backend"

Write-Host "Resetting admin credentials..."
& py -3.10 "$root\backend\app\scripts\reset_admin.py"
