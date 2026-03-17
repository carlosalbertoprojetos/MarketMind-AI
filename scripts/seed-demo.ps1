$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
$env:PYTHONPATH = "$root\backend"

Write-Host "Seeding demo data..."
& py -3.10 "$root\backend\app\scripts\seed_demo.py"
