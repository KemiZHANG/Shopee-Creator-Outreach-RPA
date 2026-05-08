$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

python -m pip install pyinstaller

python -m PyInstaller `
  --clean `
  --onefile `
  --name Shopee_Creator_Outreach_RPA `
  --paths scripts `
  scripts\run_creator_bd_rpa.py

$packageDir = Join-Path $projectRoot "release\Shopee_Creator_Outreach_RPA"
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "config") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "logs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "images\buttons") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "images\dialogs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "images\anchors") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageDir "images\reference") | Out-Null
Copy-Item "dist\Shopee_Creator_Outreach_RPA.exe" $packageDir -Force
Copy-Item "config\automation_config.example.json" (Join-Path $packageDir "config\automation_config.example.json") -Force
Copy-Item "auth_config.example.json" (Join-Path $packageDir "auth_config.example.json") -Force
Copy-Item "requirements.txt" $packageDir -Force
Copy-Item "AUTHORIZATION.md" $packageDir -Force
Copy-Item "images\template_notes.txt" (Join-Path $packageDir "images\template_notes.txt") -Force

Write-Host "Release package created:"
Write-Host $packageDir
