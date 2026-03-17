# Get the parent directory of the current script
$parentDir = Split-Path -Parent $PSScriptRoot

Write-Host "Packing parent directory: $parentDir"

# Create a temporary folder for packing
$tempFolder = Join-Path $env:TEMP "archipelago_pack_$(Get-Random)\sfa"
New-Item -ItemType Directory -Path $tempFolder | Out-Null
write-Host "Created temporary folder: $tempFolder"

# Copy client files from parent directory to temp folder
Copy-Item -Path "$parentDir\*" -Destination $tempFolder -Recurse -Force
Remove-Item -Path "$tempFolder\.git" -Recurse -Force
Remove-Item -Path "$tempFolder\.ruff_cache" -Recurse -Force
Remove-Item -Path "$tempFolder\__pycache__" -Recurse -Force
Remove-Item -Path "$tempFolder\tools" -Recurse -Force
Remove-Item -Path "$tempFolder\.gitignore" -Force
Remove-Item -Path "$tempFolder\ruff.toml" -Force
Remove-Item -Path "$tempFolder\StarFoxAdventuresLogo.png" -Force
Remove-Item -Path "$tempFolder\TODO.md" -Force
Remove-Item -Path "$tempFolder\sfa.zip" -Force

# Define the output zip file path
$zipPath = Join-Path $parentDir "sfa.zip"

# Compress the parent directory
Compress-Archive -Path $tempFolder -DestinationPath $zipPath -Force
Rename-Item -Path $zipPath -NewName "sfa.apworld"

Write-Host "Parent directory packed to: $zipPath"